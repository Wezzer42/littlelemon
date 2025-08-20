"use client";
import { ReactNode, useState } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient as qc } from "@/lib/queryClient";


export default function Providers({ children }: { children: ReactNode }) {
const [client] = useState(() => qc);
return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}