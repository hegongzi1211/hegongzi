import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

type CinematicBackgroundProps = {
  variant?: "wide" | "monitor" | "desk";
  showRobot?: boolean;
};

export const CinematicBackground: React.FC<CinematicBackgroundProps> = ({
  variant = "wide",
  showRobot = true,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const crop = variant === "monitor"
    ? { scale: 1.15, x: -42, y: 12 }
    : variant === "desk"
      ? { scale: 1.1, x: 28, y: -36 }
      : { scale: 1.04, x: 0, y: 0 };
  const driftX = crop.x + (progress - 0.5) * (variant === "monitor" ? 28 : 18);

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#070a0b" }}>
      <Img
        src={staticFile("cinematic/studio-night-v1.png")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `translate3d(${driftX}px, ${crop.y}px, 0) scale(${crop.scale + progress * 0.035})`,
          filter: "brightness(.72) saturate(.9) contrast(1.05)",
        }}
      />
      <AbsoluteFill
        style={{
          background: "linear-gradient(180deg, rgba(2,8,12,.22), rgba(2,6,8,.06) 48%, rgba(2,5,6,.68) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -80 + progress * 50,
          top: 160,
          width: 330,
          height: 980,
          transform: "rotate(-8deg)",
          background: "linear-gradient(90deg, transparent, rgba(36,205,255,.12), transparent)",
          filter: "blur(28px)",
        }}
      />
      {showRobot ? (
        <Img
          src={staticFile("cinematic/helper-robot-v1.png")}
          style={{
            position: "absolute",
            right: variant === "desk" ? -58 : -96,
            bottom: variant === "desk" ? 114 : 142,
            width: variant === "desk" ? 390 : 330,
            height: "auto",
            transform: `translateY(${Math.sin(frame / 18) * 4}px) rotate(${Math.sin(frame / 36) * 0.5}deg)`,
            transformOrigin: "50% 100%",
            mixBlendMode: "screen",
            filter: "brightness(.82) contrast(1.12) drop-shadow(0 24px 32px rgba(0,0,0,.55))",
            opacity: 0.94,
          }}
        />
      ) : null}
      <AbsoluteFill
        style={{
          background: "radial-gradient(circle at 50% 42%, transparent 42%, rgba(0,0,0,.42) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
