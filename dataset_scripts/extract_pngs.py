import os 
import cv2
import subprocess
import random
cwd = os.getcwd()
class FileTree:
    def __init__(self,originalDir):
        self.root = originalDir
        self.rootDict = {}
        self.fileList = []

    def returnFileTree(
        self,
        directory:str=None,
        ) -> list:
        """
        Traverses file structure and adds a dict to the list. {Directory: File}
        """
        for i in os.listdir(directory):

            if os.path.isfile(os.path.join(directory,i)):
                self.fileList.append([directory,i])

            else:
                
                self.returnFileTree(
                        os.path.join(self.root,directory,i) 
                        if self.root != directory 
                        else os.path.join(directory,i)
                    )
                
        return self.fileList

def returnVideoCapIfVideo(video):
    try:
        cap = cv2.VideoCapture(video)
        if cap.isOpened():
            return cap
        else:
            return False
    except cv2.error as e:
        return False

def getVideoFrameCount(video:cv2.VideoCapture) -> float:
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    return frame_count

def getVideoFPS(video:cv2.VideoCapture) -> float:
    fps = int(video.get(cv2.CAP_PROP_FPS))
    return fps


def frameToTimecode(frame_number, frame_rate):
    total_seconds = frame_number / frame_rate
    
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def extractFrame(video_path, output_path, frame_number,fps):
    try:
        # FFmpeg command to extract frame without decoding the whole video
        cmd = [
            'ffmpeg',
            '-ss', frameToTimecode(frame_number,fps),
            '-i', video_path,
            '-vframes', '1',
            '-q:v','0',
            f'{output_path}',
            '-y'
        ]
        
        # Run FFmpeg command
        subprocess.run(cmd, check=True, capture_output=True)
        
        print(f'Frame {frame_number} saved as {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'Error extracting frame {frame_number}: {e.stderr.decode()}')

def extractFrames(
                  fileList:list[list],
                  framesFromEachVideo=5,
                  writeDirectory=cwd
                  ):
    """
    extracts random frames from a list of video files
    """
    for file in fileList:
        directory = file[0]
        file = file[1]
        
        filePath = os.path.join(directory,file)
        outputFilePath = os.path.join(writeDirectory,file)
        video = returnVideoCapIfVideo(filePath)
        if video != False:
            mkdir(outputFilePath)
            frameCount = getVideoFrameCount(video)
            fps = getVideoFPS(video)
            if frameCount > 0:
                for frameNum in range(framesFromEachVideo):
                    extractFrame(filePath,os.path.join(outputFilePath,f"{frameNum}.png"),random.randint(0,frameCount),fps)
                
def mkdir(dir):
    if os.path.exists(dir):
        return
    os.makedirs(dir)

def main():
    pngOutputDir = os.path.join(cwd, "output")
    mkdir(pngOutputDir)

    filetree = FileTree(originalDir=cwd)
    filetree = filetree.returnFileTree(directory=cwd)
    extractFrames(
            filetree,
            30,
            pngOutputDir)
if __name__ == '__main__':
    main()
