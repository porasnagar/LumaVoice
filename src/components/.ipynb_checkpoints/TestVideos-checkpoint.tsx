
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Play, Eye, X, Loader2 } from 'lucide-react';
import { useTestVideos } from '@/hooks/useTestVideos';

interface TestVideosProps {
  onVideoSelect: (videoPath: string) => void;
  selectedVideo: string | null;
  onClearVideo: () => void;
}

export const TestVideos = ({ onVideoSelect, selectedVideo, onClearVideo }: TestVideosProps) => {
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [selectedVideoFile, setSelectedVideoFile] = useState<string>('');
  const [showPreview, setShowPreview] = useState(true); //false
  
  const { testData, loading, error } = useTestVideos();

  const handleFolderSelect = (folder: string) => {
    setSelectedFolder(folder);
    setSelectedVideoFile('');
    setShowPreview(true); //false
  };

  const handleVideoSelect = (video: string) => {
    setSelectedVideoFile(video);
    const fullPath = `data/recordings/data/${selectedFolder}/${video}`;
    onVideoSelect(fullPath);
  };

  const handlePreview = () => {
    setShowPreview(!showPreview);
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
        <p className="text-muted-foreground">Loading test videos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive mb-2">{error}</p>
        <p className="text-sm text-muted-foreground">
          Make sure the test video directory exists at: data/recordings/data
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Test with Saved Videos</h3>
        <p className="text-muted-foreground">
          Select videos from the test dataset (data/recordings/data)
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Select Folder</label>
          <Select value={selectedFolder} onValueChange={handleFolderSelect}>
            <SelectTrigger>
              <SelectValue placeholder="Choose test folder" />
            </SelectTrigger>
            <SelectContent>
              {testData.folders.map((folder) => (
                <SelectItem key={folder} value={folder}>
                  {folder}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Select Video</label>
          <Select 
            value={selectedVideoFile} 
            onValueChange={handleVideoSelect}
            disabled={!selectedFolder}
          >
            <SelectTrigger>
              <SelectValue placeholder="Choose video file" />
            </SelectTrigger>
            <SelectContent>
              {selectedFolder && testData.videos[selectedFolder]?.map((video) => (
                <SelectItem key={video} value={video}>
                  {video}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {selectedVideo && (
        <Card className="p-4 bg-muted/20">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Play className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Selected: {selectedVideo}</span>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreview}
                className="text-xs"
              >
                <Eye className="w-3 h-3 mr-1" />
                {showPreview ? 'Hide' : 'Preview'}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearVideo}
                className="text-xs"
              >
                <X className="w-3 h-3 mr-1" />
                Clear
              </Button>
            </div>
          </div>

          {showPreview && (
            <div className="mt-4 p-4 border border-border rounded-lg bg-background/50">
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <Eye className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">Video Preview</p>
                  <p className="text-xs">Path: {selectedVideo}</p>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};
