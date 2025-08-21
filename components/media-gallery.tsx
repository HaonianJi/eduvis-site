export default function MediaGallery() {
  return (
    <div className="flex justify-center">
      <div className="w-full max-w-4xl aspect-video bg-muted rounded-lg overflow-hidden">
        <iframe
          src="https://platform.twitter.com/embed/Tweet.html?id=1938794758258008151"
          className="w-full h-full border-0"
          title="EduVisAgent Demo Video"
          allowFullScreen
        />
      </div>
    </div>
  )
}
