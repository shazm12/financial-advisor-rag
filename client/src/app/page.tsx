"use client";
import { useEffect, useRef } from "react";
import gsap from 'gsap';
import InputBox from "@/components/inputbox";


export default function Home() {
  const titleRef = useRef<HTMLHeadingElement>(null);

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
        ease: "elastic.out(1, 0.5)" // More wind-like bounce
      }
    )
  }, [])

  return (
    <main className="min-h-screen flex flex-col items-center justify-center">
      <h1 ref={titleRef} className="text-4xl font-bold">ReMoney</h1>
      <InputBox />
    </main>
  );
}
