import { useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Camera, Square, Play, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface WebcamRecorderProps {
  onVideoRecord: (blob: Blob) => void;
  recordedVideo: Blob | null;
  onClearVideo: () => void;
}

export const WebcamRecorder = ({ onVideoRecord, recordedVideo, onClearVideo }: WebcamRecorderProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const { toast } = useToast();

  const startWebcam = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (error) {
      toast({
        title: "Camera access denied",
        description: "Please allow camera access to record video",
        variant: "destructive"
      });
    }
  }, [toast]);

  const stopWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, [stream]);

  const startRecording = useCallback(() => {
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      onVideoRecord(blob);
      
      // Create preview URL
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      
      stopWebcam();
      setIsRecording(false);
    };

    mediaRecorder.start();
    setIsRecording(true);
  }, [stream, onVideoRecord, stopWebcam]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  }, [isRecording]);

  const clearRecording = useCallback(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    onClearVideo();
    stopWebcam();
  }, [previewUrl, onClearVideo, stopWebcam]);

  return (
    <Card className="glass-card p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-accent">
          <Camera className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Record Video</h3>
        </div>

        <div className="aspect-video glass rounded-lg overflow-hidden relative">
          {recordedVideo && previewUrl ? (
            <video
              src={previewUrl}
              controls
              className="w-full h-full object-cover"
            />
          ) : (
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover"
            />
          )}
          
          {!stream && !recordedVideo && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Camera className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Click "Start Camera" to begin</p>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          {!stream && !recordedVideo && (
            <Button onClick={startWebcam} variant="glass">
              <Camera className="w-4 h-4" />
              Start Camera
            </Button>
          )}

          {stream && !isRecording && !recordedVideo && (
            <>
              <Button onClick={startRecording} variant="gradient">
                <Play className="w-4 h-4" />
                Start Recording
              </Button>
              <Button onClick={stopWebcam} variant="ghost">
                Cancel
              </Button>
            </>
          )}

          {isRecording && (
            <Button onClick={stopRecording} variant="destructive">
              <Square className="w-4 h-4" />
              Stop Recording
            </Button>
          )}

          {recordedVideo && (
            <Button
              onClick={clearRecording}
              variant="ghost"
              className="text-destructive hover:text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="w-4 h-4" />
              Clear Recording
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};