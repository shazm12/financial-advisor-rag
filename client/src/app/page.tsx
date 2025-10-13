"use client";
import { useEffect, useRef, useState } from "react";
import gsap from 'gsap';
import FileUploader from "@/components/fileuploader";
import ChatInterface from "@/components/chatinterface";
import { Button } from "@/components/ui/button";
import AnimatedText from "@/components/animatedtext";
import { uploadDocToAPI } from "@/actions/upload-doc";
import { toast } from "sonner";

type Step = "upload" | "chat";

export default function Home() {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const imgContainerRef = useRef<HTMLDivElement>(null);
  const subTitleRef = useRef<HTMLHeadingElement>(null);
  const [currentStep, setCurrentStep] = useState<Step>("upload");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  useEffect(() => {
    gsap.fromTo(
      titleRef.current,
      {
        x: -300,
        opacity: 0,
        scale: 0.8,
        rotation: -10
      },
      {
        x: 0,
        opacity: 1,
        scale: 1,
        rotation: 0,
        duration: 4,
        ease: "elastic.out(1, 0.5)"
      }
    );
  }, []);

  useEffect(() => {
    if (!imgContainerRef.current) return;

    const img = imgContainerRef.current.querySelector('img');

    if (img) {

      gsap.set(img, { opacity: 0, x: 0 });
      const tl = gsap.timeline();

      tl.to(img, {
        opacity: 1,
        duration: 0.5,
        delay: 6
      })
        .to(img, {
          x: -5,
          duration: 0.8,
          yoyo: true,
          ease: "power1.inOut",
          repeat: -1
        });
    }

  }, []);

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    const response = await uploadDocToAPI(file);
    if (response.success) {
      toast.success(response.description || "File Upload Successful", { position: "bottom-right", duration: 4000 });
    }
    if (!response.success && response.error) {
      toast.error(response.error || "Error in File Upload!", { position: "bottom-right", duration: 4000 });
      return;
    }
    gsap.to(".content-wrapper", {
      opacity: 0,
      y: -20,
      duration: 0.3,
      onComplete: () => {
        setCurrentStep("chat");
        gsap.fromTo(".content-wrapper",
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.5 }
        );
      }
    });
  };

  const handleReset = () => {
    setCurrentStep("upload");
    setUploadedFile(null);
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 ref={titleRef} className="text-4xl font-bold mb-8">ReMoney</h1>
      <div ref={imgContainerRef} className="flex flex-row gap-4 items-center justify-center w-full mb-4">
        <AnimatedText delay={5} text="Financial wisdom, personalized for you" className="mb-0" />
        <img src="/icons/money.svg" alt="money-icon" width={32} height={32} />
      </div>
      {/* Progress Indicator */}
      <div className="flex items-center gap-2 mb-8">
        <div className={`w-3 h-3 rounded-full ${currentStep === "upload" ? "bg-blue-600" : "bg-green-600"}`} />
        <div className={`w-20 h-1 ${currentStep === "chat" ? "bg-blue-600" : "bg-slate-300"}`} />
        <div className={`w-3 h-3 rounded-full ${currentStep === "chat" ? "bg-blue-600" : "bg-slate-300"}`} />
      </div>

      <div className="content-wrapper w-full flex justify-center">
        {currentStep === "upload" && (
          <FileUploader onFileUpload={handleFileUpload} />
        )}

        {currentStep === "chat" && uploadedFile && (
          <div className="space-y-2">
            <Button variant="outline" onClick={handleReset} className="w-full">
              Upload Different File
            </Button>
            <ChatInterface fileName={uploadedFile.name} />
          </div>
        )}
      </div>
    </main>
  );
}
