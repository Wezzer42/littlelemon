"use client";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export type Me = {
  id: number; username: string; email: string;
  is_manager: boolean; is_delivery: boolean; is_staff: boolean; is_superuser: boolean;
};

export function useMe(enabled = true) {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/api/me")).data as Me,
    enabled,
    staleTime: 60_000,
  });
}
