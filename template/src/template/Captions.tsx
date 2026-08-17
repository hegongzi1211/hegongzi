import { useCurrentFrame, useVideoConfig } from "remotion";
import type { CaptionData } from "./types";

export const Captions: React.FC<{ captions: CaptionData[]; hideBeforeFrame: number; narrationStartFrame: number }> = ({ captions, hideBeforeFrame, narrationStartFrame }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const nowMs = (frame - narrationStartFrame) / fps * 1000;
  if (frame < hideBeforeFrame) return null;
  const caption = captions.find((item) => nowMs >= item.startMs && nowMs < item.endMs);
  if (!caption) return null;
  const text = caption.text.replace(/^[，。！？、；：,.!?;:\s]+/, "");
  const fontSize = 42;

  return (
    <div style={{
      position: "absolute",
      left: 150,
      right: 150,
      bottom: 92,
      height: 132,
      padding: "14px 32px",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "#fff",
      fontFamily: "'PingFang SC', sans-serif",
      fontSize,
      lineHeight: 1.16,
      fontWeight: 900,
      textAlign: "center",
      whiteSpace: "normal",
      wordBreak: "normal",
      overflowWrap: "break-word",
      overflow: "hidden",
      maxHeight: 132,
      border: "1px solid rgba(32,235,151,.70)",
      borderRadius: 24,
      background: "rgba(0,12,10,.62)",
      boxShadow: "0 0 26px rgba(32,235,151,.16), inset 0 0 22px rgba(32,235,151,.05)",
      textShadow: "0 4px 16px rgba(0,0,0,.94), 0 0 5px rgba(0,0,0,.98)",
      zIndex: 100,
    }}>
      <span style={{
        display: "-webkit-box",
        WebkitBoxOrient: "vertical",
        WebkitLineClamp: 2,
        overflow: "hidden",
      }}>
        {text}
      </span>
    </div>
  );
};
