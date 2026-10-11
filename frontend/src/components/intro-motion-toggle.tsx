"use client";
import { useEffect, useState } from "react";
import { Pause, Play } from "lucide-react";
import styles from "../app/intro.module.css";

export function IntroMotionToggle() {
  const [paused, setPaused] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(preference.matches);
    update();
    preference.addEventListener("change", update);
    return () => preference.removeEventListener("change", update);
  }, []);
  const stopped = paused || reducedMotion;
  const label = reducedMotion
    ? "Background animation off: reduced motion enabled on your device"
    : paused
      ? "Resume background animation"
      : "Pause background animation";
  return (
    <button
      className={styles.motionToggle}
      data-paused={stopped}
      disabled={reducedMotion}
      aria-label={label}
      title={label}
      onClick={() => setPaused((value) => !value)}
    >
      {stopped ? <Play size={16} /> : <Pause size={16} />}
    </button>
  );
}
