import yt_dlp
import os
from pydub import AudioSegment # chunking ke time use hogi,pydub ka kaam audio files ko cut karna, merge karna, format badalna (jaise WAV se MP3), ya volume kam/zyada karna hota hai
#EK FOLDER JISKE ANDAR SARI CHEEZEIN SAVE HO JAISEY YOUTUBE SE AUDIO DOWNLOAD USKO KAHIN PE SAVE KARNA PARE GA
DOWNLOAD_DIR="downloads" # ab ye downloads folder ke andar save 
os.makedirs(DOWNLOAD_DIR, exist_ok=True) #agar folder exist nahi karta toh create kar do,agar exist karta hai toh kuch mat karo
def download_audio_from_youtube(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s") # ye template hamein file ka naam aur extension dega, jaisey file naam hai test.mp3 toh ye test.mp3 ke naam se save hoga test jaye ga text mein or mp3 jaye ga ext mein
    ydl_opts = {
        'format': 'bestaudio/best', # best audio quality
        'outtmpl': output_path, # output template
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', # extract audio using ffmpeg
            'preferredcodec': 'wav', # convert to wav
            'preferredquality': '192', # 192 kbps quality
        }],
        "quiet": True, # exit after download
        "socket_timeout": 30,     # zyada time do connection ke liye
        "retries": 10,            # zyada retries
        "fragment_retries": 10,
    }  
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: #youtubedl ek engine hai jo download,extraction,convertion wagera karta hai ye yt-dlp ki hi ek class hai hamne isko apna naqsa opts deya or ek object bana deya takeh ab jo be cheez nekalni jaisy info wo us naqshe ke mutabik ho or wo sari cheezein directory mein save hon
        info=ydl.extract_info(url,download=True) #information extract karne ke liye
        filename=ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
        return filename
        
        #Isi dictionary ko prepare_filename(info) use karta hai taake title aur ext (jaisi keys) se filename banaye — matlab info mein se hi wo data nikal ke pattern (%(title)s.%(ext)s) fill karta hai.
        #
#data=download_audio_from_youtube("https://www.youtube.com/watch?v=mtiOK2QG9Q0")       
#extract_info() do kaam ek sath karta hai:
# ydl_opts (naqsha) follow karta hai → download, mp3 conversion sab ho jata hai
# YouTube se video ka detail (info dict) bhi deta hai — title, ext, duration, etc.

# Lekin info ke andar jo ext hai wo video ki original extension hai (jaise webm/m4a) — postprocessor ne jo baad mein convert kiya (mp3), wo update nahi hota info mein.
# prepare_filename(info) isi original title + ext use kar ke naam banata hai — is liye purani extension aati hai, aur humein manually .replace() kar ke asal (converted) extension set karni padti hai.
  
  
    
def convert_audio_to_wav(input_file: str) -> str:
    output_file = os.path.splitext(input_file)[0] + ".wav" # os.path.splitext() input_file ko do parts mein todta hai: (filename, extension). [0] matlab sirf filename le lo aur .wav add kar do
    audio = AudioSegment.from_file(input_file) # pydub ka AudioSegment class use karke input_file ko load karte hain
    audio= audio.set_channels(1).set_frame_rate(16000) # mono channel set karte hain
    audio.export(output_file, format="wav") # export method se audio ko wav format mein save karte hain, audio ko wav file mein disk pe save karta hai.
    return output_file
#final_data=convert_audio_to_wav(data) # yaha agar koi song parha jaisey song.mp3 direct uska yaha convert_audio_to_wav() method call karenge toh wo song.wav ke naam se convert ho jaye ga aur mono channel mein 16kHz frame rate ke sath save ho jaye ga
#ye for file be work karti ke jab apko youtube se audio na uthani ho direct apke pc ke file mein ho

def chunk_audio(wave_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wave_path) #AudioSegment.from_wav() pydub ka method hai jo ek .wav file ko load karke ek AudioSegment object mein convert karta hai — taaki tum us audio ko slice/chunk, export, ya manipulate kar sako code mein.
#Short mein: wav file read karke usable audio object bana deta hai.
    chunk_ms=chunk_minutes * 60 * 1000 # convert minutes to milliseconds
    chunks = []
    for i ,start in enumerate(range(0, len(audio), chunk_ms)): # audio ko chunk_ms ke hisaab se slice karte hain
        chunk=audio[start:start + chunk_ms]
        chunk_path=f"{wave_path}_chunk_{i}.wav" # chunk ka naam wave_path ke sath index laga ke banate hain
        chunk.export(chunk_path, format="wav") #Haan, bilkul sahi socha — chunk.export(...) wala chunk, chunk=audio[start:start + chunk_ms] wala hi variable hai.Same variable hai, jo har loop iteration mein naya audio slice store karta hai, aur usi pe .export() call ho raha hai.yani har chunk ko wo wav bana raha 
        chunks.append(chunk_path) # chunk ka path list mein add karte hain
    return chunks
#print(chunk_audio(final_data)) 


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("download youtube audio....")
        audio_file = download_audio_from_youtube(source)
    else:
        print("detecting local audio file, converting to wav....")
        audio_file = convert_audio_to_wav(source)

    print("chunking audio....")
    chunks = chunk_audio(audio_file)
    print(f"Audio file chunked into {len(chunks)} parts.")
    return chunks   # <-- ye line function ke end mein, dono branches ke bahar honi chahiye
