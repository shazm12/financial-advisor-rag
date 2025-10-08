import { useEffect, useRef } from "react";
import SplitType from "split-type";
import gsap from "gsap";

interface AnimatedTextProps {
    text: string;
    delay?: number;
    className?: string;
}

export default function AnimatedText({ text, delay = 0, className = "" }: AnimatedTextProps) {
    const textRef = useRef<HTMLHeadingElement>(null);

    useEffect(() => {
        if (!textRef.current) return;
        const split = new SplitType(textRef.current, { types: "chars" });

        gsap.from(split.chars, {
            x: -50,
            opacity: 0,
            duration: 0.6,
            delay: delay,
            ease: "power3.out",
            stagger: 0.03
        });

        return () => {
            split.revert();
        };

    }, [delay]);

    return (
        <h1
            ref={textRef}
            className={`hero-text text-2xl font-semibold text-gray-900 ${className}`}
        >
            {text}
        </h1>
    );
}
