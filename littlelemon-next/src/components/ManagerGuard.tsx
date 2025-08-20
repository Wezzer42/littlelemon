"use client";
import { useEffect } from "react";
import { useMe } from "@/lib/useMe";
import { isAuthed } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function ManagerGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data, isLoading, isError } = useMe(isAuthed());

  useEffect(() => {
    if (!isAuthed()) router.replace("/login");
  }, [router]);

  if (!isAuthed() || isLoading) return null;
  if (isError || !data?.is_manager) {
    router.replace("/");
    return null;
  }
  return <>{children}</>;
}
