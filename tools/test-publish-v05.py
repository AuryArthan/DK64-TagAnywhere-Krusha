"""Offline safety checks; never contact GitHub."""
import contextlib, importlib.util, io, json, os, unittest, urllib.error
from pathlib import Path
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('publisher', Path(__file__).with_name('publish-v05.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

class Response:
    def __init__(self, value): self.data = json.dumps(value).encode()
    def __enter__(self): return io.BytesIO(self.data)
    def __exit__(self, *args): pass

class PublisherTests(unittest.TestCase):
    def run_publisher(self, handler):
        with patch.dict(os.environ, {'GH_TOKEN':'offline-test-token', 'GITHUB_REPOSITORY':p.REPO}), patch('sys.argv',['publish']), patch.object(p.urllib.request,'urlopen',side_effect=handler), contextlib.redirect_stdout(io.StringIO()):
            p.main()

    def test_upload_exact_bytes_rename_then_publish(self):
        calls=[];data=p.validate()
        def server(req,timeout):
            calls.append(req)
            if len(calls)==1:raise urllib.error.HTTPError(req.full_url,404,'missing',{},None)
            if len(calls)==2:return Response({'id':1,'draft':True,'assets':[],'upload_url':'https://uploads.github.com/repos/'+p.REPO+'/releases/1/assets{?name}'})
            if len(calls)==3:
                self.assertEqual(req.data,data);self.assertIn('%2B',req.full_url)
                return Response({'id':2,'name':'normalized.bps','size':len(data),'digest':'sha256:'+p.SHA})
            if len(calls)==4:
                self.assertEqual(json.loads(req.data),{'name':p.NAME})
                return Response({'id':2,'name':p.NAME,'size':len(data),'digest':'sha256:'+p.SHA,'browser_download_url':'asset'})
            self.assertEqual(json.loads(req.data),{'draft':False,'make_latest':'true'})
            return Response({'html_url':'release','draft':False})
        self.run_publisher(server);self.assertEqual(len(calls),5)

    def test_existing_unverified_asset_is_not_overwritten(self):
        calls=[]
        def server(req,timeout):
            calls.append(req);return Response({'assets':[{'name':p.NAME,'digest':'sha256:wrong'}]})
        with self.assertRaisesRegex(RuntimeError,'left untouched'):self.run_publisher(server)
        self.assertEqual(len(calls),1)

    def test_unpreserved_plus_sign_stays_draft(self):
        calls=[];data=p.validate()
        def server(req,timeout):
            calls.append(req)
            if len(calls)==1:return Response({'id':1,'draft':True,'assets':[],'upload_url':'https://uploads.github.com/repos/'+p.REPO+'/releases/1/assets{?name}'})
            return Response({'id':2,'name':'normalized.bps','size':len(data)})
        with self.assertRaisesRegex(RuntimeError,'Draft was not published'):self.run_publisher(server)
        self.assertEqual(len(calls),3)
        self.assertFalse(any('/releases/1'==r.full_url.removeprefix(p.BASE) and r.method=='PATCH' for r in calls))

    def test_wrong_patch_fails_before_network(self):
        with patch.object(p,'SHA','0'*64),patch.object(p.urllib.request,'urlopen') as network:
            with self.assertRaises(RuntimeError):p.validate()
            network.assert_not_called()

    def test_wrong_tag_fails_before_network(self):
        with patch.object(p.subprocess, 'check_output', return_value='0'*40), patch.object(p.urllib.request, 'urlopen') as network:
            with self.assertRaisesRegex(RuntimeError, 'never recreate or move'):
                p.validate()
            network.assert_not_called()

if __name__=='__main__':unittest.main()
