"use client";
import { useState, useEffect } from "react";
import { motion, useReducedMotion } from "motion/react";
import {
  Orbit,
  ScanText,
  Files,
  Link as LinkIcon,
  LifeBuoy,
  AlignLeft,
  Video as Youtube,
  Newspaper,
  ScanLine,
  Image as ImageIcon,
  AudioLines,
  Captions,
  SquareCode,
  Layers,
  Search,
  Settings2,
  Sun,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Menu,
  ArrowRight,
  ArrowUpRight,
  Plus,
  X,
  FileText,
  Upload,
  AlertTriangle,
  Command,
  ExternalLink,
  ChevronRight,
  BookOpen,
} from "lucide-react";
const toolIcons = {
  Orbit,
  ScanText,
  Files,
  Link: LinkIcon,
  LifeBuoy,
  AlignLeft,
  Youtube,
  Newspaper,
  FileText,
  ScanLine,
  Image: ImageIcon,
  AudioLines,
  Captions,
  SquareCode,
  Layers,
};
export function ToolIcon({ name, size = 17 }: { name: string; size?: number }) {
  const Icon = toolIcons[name as keyof typeof toolIcons] || FileText;
  return <Icon size={size} strokeWidth={1.65} />;
}
export function AttachmentPreview({ files }: { files: File[] }) {
  const reduced = useReducedMotion();
  const [image, setImage] = useState("");
  useEffect(() => {
    const file = files[0];
    if (!file || !file.type.startsWith("image/")) {
      setImage("");
      return;
    }
    const url = URL.createObjectURL(file);
    setImage(url);
    return () => URL.revokeObjectURL(url);
  }, [files]);
  return image ? (
    <motion.div
      layout={!reduced}
      transition={{ duration: 0.26 }}
      className="attachment-preview"
    >
      <img src={image} alt={`Input preview: ${files[0].name}`} />
    </motion.div>
  ) : null;
}
