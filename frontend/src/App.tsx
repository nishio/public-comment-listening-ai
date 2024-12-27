import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import { Eye, EyeOff, Send } from "lucide-react";

interface Comment {
  content: string;
  key_points: string[];
  is_public: boolean;
}

function App() {
  const [content, setContent] = useState("");
  const [comments, setComments] = useState<Comment[]>([]);
  const [showPrivate, setShowPrivate] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedPoints, setExtractedPoints] = useState<string[]>([]);
  const [showSubmitButton, setShowSubmitButton] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [showPrivate]);

  const handleExtractPoints = async () => {
    if (!content.trim()) return;
    
    setIsExtracting(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });
      
      if (!response.ok) throw new Error('要点抽出に失敗しました');
      
      const points = await response.json();
      setExtractedPoints(points);
      setShowSubmitButton(true);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSubmit = async () => {
    if (!content.trim() || !extractedPoints.length) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });
      
      if (!response.ok) throw new Error('送信に失敗しました');
      
      await response.json();
      setContent("");
      setExtractedPoints([]);
      setShowSubmitButton(false);
      fetchComments();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/comments?show_private=${showPrivate}`);
      if (!response.ok) throw new Error('コメントの取得に失敗しました');
      const data = await response.json();
      setComments(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const toggleVisibility = async (commentId: number, isPublic: boolean) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/comments/${commentId}/visibility`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_public: isPublic }),
      });
      fetchComments();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>パブリックコメント投稿</CardTitle>
          <CardDescription>
            投稿内容は公開されます。個人情報は含めないでください。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="コメントを入力してください"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="mb-4"
            rows={6}
          />
          <div className="space-y-4">
            <Button
              onClick={handleExtractPoints}
              disabled={isExtracting || !content.trim()}
              className="w-full"
            >
              要点を確認
              {isExtracting && '中...'}
            </Button>
            
            {extractedPoints.length > 0 && (
              <Alert>
                <AlertDescription>
                  <div className="font-bold mb-2">抽出された要点：</div>
                  <ul className="list-disc pl-4">
                    {extractedPoints.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {showSubmitButton && (
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="w-full"
              >
                <Send className="mr-2 h-4 w-4" />
                {isSubmitting ? '送信中...' : '送信'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>



      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">投稿一覧</h2>
        <div className="flex items-center space-x-2">
          <span>非公開コメントを表示</span>
          <Switch
            checked={showPrivate}
            onCheckedChange={setShowPrivate}
          />
        </div>
      </div>

      <div className="space-y-4">
        {comments.map((comment, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <p className="whitespace-pre-wrap">{comment.content}</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => toggleVisibility(index, !comment.is_public)}
                >
                  {comment.is_public ? (
                    <Eye className="h-4 w-4" />
                  ) : (
                    <EyeOff className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="border-t pt-4">
                <div className="font-bold mb-2">要点：</div>
                <ul className="list-disc pl-4">
                  {comment.key_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default App
