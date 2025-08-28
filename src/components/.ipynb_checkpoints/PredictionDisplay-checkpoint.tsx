import { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { MessageSquare, Volume2, Loader2, Play } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface PredictionDisplayProps {
  prediction: string;
  isLoading: boolean;
}

export const PredictionDisplay = ({ prediction, isLoading }: PredictionDisplayProps) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const { toast } = useToast();

  const handleSpeak = async () => {
    if (!prediction || isSpeaking) return;

    // Check if browser supports Speech Synthesis
    if (!('speechSynthesis' in window)) {
      toast({
        title: "Speech not supported",
        description: "Your browser doesn't support text-to-speech",
        variant: "destructive"
      });
      return;
    }

    setIsSpeaking(true);

    try {
      // Cancel any ongoing speech
      speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(prediction);
      
      // Configure speech settings
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;

      // Try to use a more natural voice if available
      const voices = speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith('en') && voice.name.includes('Google')
      ) || voices.find(voice => voice.lang.startsWith('en'));
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      utterance.onend = () => {
        setIsSpeaking(false);
      };

      utterance.onerror = () => {
        setIsSpeaking(false);
        toast({
          title: "Speech error",
          description: "Failed to convert text to speech",
          variant: "destructive"
        });
      };

      speechSynthesis.speak(utterance);
    } catch (error) {
      setIsSpeaking(false);
      toast({
        title: "Speech error",
        description: "Failed to convert text to speech",
        variant: "destructive"
      });
    }
  };

  const stopSpeaking = () => {
    speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return (
    <Card className="p-6 bg-gradient-card border-border/50">
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-accent">
          <MessageSquare className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Prediction Result</h3>
        </div>

        <div className="min-h-[120px] p-4 bg-muted/20 rounded-lg border border-border/30">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-3">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
                <span className="text-muted-foreground">Analyzing lip movements...</span>
              </div>
            </div>
          ) : prediction ? (
            <div className="space-y-4">
              <p className="text-lg leading-relaxed">{prediction}</p>
              <div className="flex gap-2">
                {!isSpeaking ? (
                  <Button onClick={handleSpeak} variant="gradient" size="sm">
                    <Volume2 className="w-4 h-4" />
                    Speak
                  </Button>
                ) : (
                  <Button onClick={stopSpeaking} variant="destructive" size="sm">
                    <Play className="w-4 h-4 rotate-180" />
                    Stop Speaking
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>Upload a video and click "Predict" to see the results</p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};