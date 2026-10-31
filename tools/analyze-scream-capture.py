#!/usr/bin/env python3
"""Compare each captured stereo channel directly with TheScream3, after rate conversion.
The source has no EQ/echo/layer processing. Permit tiny N64 DAC clock rounding.
"""
from pathlib import Path
import hashlib,json,math,wave,subprocess,argparse
import numpy as np
ROOT=Path(__file__).resolve().parent.parent

def pcm(path):
 with wave.open(str(path),'rb') as w:
  rate=w.getframerate();channels=w.getnchannels();assert w.getsampwidth()==2
  a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,channels)
 return rate,a

def analyze(capture,profile):
 rate,y=pcm(capture);assert rate==22050 and y.shape[1]==2
 meta=json.loads((ROOT/'assets/krusha/scream.json').read_text())
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'input_files/TheScream3.wav'),'-ac','2','-ar','22050','-f','s16le','-c:a','pcm_s16le','pipe:1'])
 x=np.frombuffer(raw,dtype='<i2').astype(float).reshape(-1,2)
 power=[np.r_[0,np.cumsum(y[:,ch]**2)] for ch in (0,1)]
 def match(scale):
  rows=[];n=int(len(x)*scale);fft_len=1<<(len(y)+n-1).bit_length()
  for ch in (0,1):
   source=np.interp(np.arange(n)/scale,np.arange(len(x)),x[:,ch]);source-=source.mean()
   energy=np.dot(source,source)
   c=np.fft.irfft(np.fft.rfft(y[:,ch],fft_len)*np.conj(np.fft.rfft(source,fft_len)),fft_len)[:len(y)-n+1]
   norm=np.sqrt(np.maximum(1,(power[ch][n:]-power[ch][:-n])*energy));corr=c/norm;i=int(np.argmax(corr))
   rows.append({'correlation':float(corr[i]),'start_sample':i,'start_seconds':i/rate,'fitted_gain':float(c[i]/energy)})
  return {'time_scale':float(scale),'channels':rows,'mean_correlation':sum(r['correlation'] for r in rows)/2}
 best=max((match(s) for s in np.linspace(.998,1.002,17)),key=lambda r:r['mean_correlation'])
 best=max([best]+[match(s) for s in np.linspace(best['time_scale']-.00015,best['time_scale']+.00015,41)],key=lambda r:r['mean_correlation'])
 quality=[]
 for ch,name in enumerate(('left','right')):
  _,decoded=pcm(ROOT/f'assets/krusha/TheScream-{name}-decoded.wav')
  reference=x[:,ch]*meta['joint_normalization_gain'];n=min(len(reference),len(decoded));reference=reference[:n];decoded=decoded[:n,0]
  error=decoded-reference
  quality.append({'channel':name,'correlation':float(np.corrcoef(reference,decoded)[0,1]),'snr_db':float(10*np.log10(np.dot(reference,reference)/np.dot(error,error))),'decoded_peak':float(np.abs(decoded).max())})
 ceiling_samples=int(np.isin(y,[-26112,26111]).sum())
 report={'rom_sha256':hashlib.sha256((ROOT/'rom/dk64-krusha-dev.z64').read_bytes()).hexdigest(),'capture':str(capture.relative_to(ROOT)),'sample_rate':rate,'stereo':True,'duration_seconds':len(y)/rate,'peak':float(np.abs(y).max()),'peak_normalized':float(np.abs(y).max()/32768),'native_mixer_ceiling_samples_after_sdl_80_percent_volume':ceiling_samples,'source_match':best,'minimum_gameplay_detection_correlation':.80,'recording_detected_in_gameplay_mix':all(r['correlation']>.80 for r in best['channels']),'encoded_source_quality':quality,'encoded_source_match_passed':all(q['correlation']>.999 for q in quality),'decoded_peak_safe':all(q['decoded_peak']<=32767*10**(meta['peak_ceiling_dbfs']/20) for q in quality),'synchronized_channels':abs(best['channels'][0]['start_sample']-best['channels'][1]['start_sample'])<=1,'no_native_mixer_clipping':ceiling_samples==0,'note':'Compare against only resampled original left/right channels. The N64 adds its required VADPCM encoding and the game retains background audio. Gameplay correlation detects the recording in that mixed signal; the separate decoded-source comparison verifies fidelity above 0.999. Native voice level, original pitch, hard stereo pan and absence of added effects are checked in the controller tests.'}
 return report

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('capture',nargs='?',type=Path);args=parser.parse_args();profile=(ROOT/'runtime/krusha/current').resolve()
 capture=(args.capture or profile/'audio/krusha-roar-scream.wav').resolve();report=analyze(capture,profile)
 dest=profile/'audio'/(capture.stem+'-analysis.json');dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 assert report['recording_detected_in_gameplay_mix'] and report['encoded_source_match_passed'] and report['decoded_peak_safe'] and report['synchronized_channels'] and report['no_native_mixer_clipping']
if __name__=='__main__':main()
