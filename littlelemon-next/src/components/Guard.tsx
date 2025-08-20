"use client";
import { isAuthed } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";


export default function Guard({ children }: { children: React.ReactNode }) {
const router = useRouter();
useEffect(() => { if (!isAuthed()) router.replace("/login"); }, [router]);
if (!isAuthed()) return null;
return <>{children}</>;
}