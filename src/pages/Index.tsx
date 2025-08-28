import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { VideoUpload } from '@/components/VideoUpload';
import { WebcamRecorder } from '@/components/WebcamRecorder';
import { TestVideos } from '@/components/TestVideos';
import { PredictionDisplay } from '@/components/PredictionDisplay';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Video, Upload, Camera, Play, Brain, Waves } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://35.201.249.96:5000';

const Index = () => {
  const [uploadedVideo, setUploadedVideo] = useState<File | null>(null);
  const [recordedVideo, setRecordedVideo] = useState<Blob | null>(null);
  const [testVideo, setTestVideo] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleVideoUpload = (file: File) => {
    setUploadedVideo(file);
    setRecordedVideo(null);
    setTestVideo(null);
    setPrediction('');
  };

  const handleVideoRecord = (blob: Blob) => {
    setRecordedVideo(blob);
    setUploadedVideo(null);
    setTestVideo(null);
    setPrediction('');
  };

  const handleTestVideoSelect = (videoPath: string) => {
    setTestVideo(videoPath);
    setUploadedVideo(null);
    setRecordedVideo(null);
    setPrediction('');
  };

  const clearUploadedVideo = () => {
    setUploadedVideo(null);
    setPrediction('');
  };

  const clearRecordedVideo = () => {
    setRecordedVideo(null);
    setPrediction('');
  };

  const clearTestVideo = () => {
    setTestVideo(null);
    setPrediction('');
  };

  const handlePredict = async () => {
    const videoToSend = uploadedVideo || recordedVideo;

    if (!videoToSend && !testVideo) {
      toast({
        title: 'No video selected',
        description: 'Please choose a video to analyze',
        variant: 'destructive'
      });
      return;
    }

    setIsLoading(true);
    setPrediction('');

    try {
      const formData = new FormData();

      if (uploadedVideo) {
        formData.append('video', uploadedVideo);
      } else if (recordedVideo) {
        const file = new File([recordedVideo], 'recorded-video.webm', {
          type: recordedVideo.type
        });
        formData.append('video', file);
      } else if (testVideo) {
        formData.append('test_path', testVideo);
      }

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data.prediction || 'No prediction available');

      toast({
        title: 'Analysis complete',
        description: 'Lip reading analysis finished successfully'
      });
    } catch (error) {
      console.error('Prediction error:', error);
      toast({
        title: 'Prediction failed',
        description: 'Server error. Please check backend logs or video format.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative">
      <header className="glass border-b border-border/50 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                <Video className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">LumaVoice</h1>
                <p className="text-sm text-muted-foreground">AI Lip Reading</p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full mb-6">
            <Brain className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered Analysis</span>
          </div>
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
            Advanced Lip Reading Technology
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload videos, record webcam footage, or test with sample videos to experience cutting-edge AI lip reading capabilities.
          </p>
        </div>

        <div className="glass-card p-8 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <Waves className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Choose Input Method</h3>
          </div>

          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-3 glass p-1">
              <TabsTrigger value="upload" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Upload className="w-4 h-4 mr-2" /> Upload
              </TabsTrigger>
              <TabsTrigger value="record" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Camera className="w-4 h-4 mr-2" /> Record
              </TabsTrigger>
              <TabsTrigger value="test" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Play className="w-4 h-4 mr-2" /> Test
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="mt-6">
              <VideoUpload onVideoSelect={handleVideoUpload} selectedVideo={uploadedVideo} onClearVideo={clearUploadedVideo} />
            </TabsContent>

            <TabsContent value="record" className="mt-6">
              <WebcamRecorder onVideoRecord={handleVideoRecord} recordedVideo={recordedVideo} onClearVideo={clearRecordedVideo} />
            </TabsContent>

            <TabsContent value="test" className="mt-6">
              <TestVideos onVideoSelect={handleTestVideoSelect} selectedVideo={testVideo} onClearVideo={clearTestVideo} />
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex justify-center mb-8">
          <Button onClick={handlePredict} disabled={(!uploadedVideo && !recordedVideo && !testVideo) || isLoading} size="lg" className="glass-button px-8 py-3 text-base font-medium">
            <Brain className="w-5 h-5 mr-2" />
            {isLoading ? 'Analyzing...' : 'Analyze Video'}
          </Button>
        </div>

        <PredictionDisplay prediction={prediction} isLoading={isLoading} />

        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <Card className="glass-card p-6 text-center">
            <div className="w-12 h-12 bg-primary/20 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">High Accuracy</h3>
            <p className="text-sm text-muted-foreground">Advanced neural networks deliver precise lip reading results</p>
          </Card>

          <Card className="glass-card p-6 text-center">
            <div className="w-12 h-12 bg-accent/20 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Waves className="w-6 h-6 text-accent" />
            </div>
            <h3 className="font-semibold mb-2">Real-time Processing</h3>
            <p className="text-sm text-muted-foreground">Fast video analysis with instant text generation</p>
          </Card>

          <Card className="glass-card p-6 text-center">
            <div className="w-12 h-12 bg-secondary/20 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <Video className="w-6 h-6 text-secondary" />
            </div>
            <h3 className="font-semibold mb-2">Multiple Formats</h3>
            <p className="text-sm text-muted-foreground">Support for various video formats and recording options</p>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Index;
