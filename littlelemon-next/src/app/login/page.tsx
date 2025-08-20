"use client";
import { useState } from "react";
import { login } from "@/lib/auth";
import { useRouter } from "next/navigation";


export default function LoginPage() {
const [username, setU] = useState("");
const [password, setP] = useState("");
const [err, setErr] = useState("");
const router = useRouter();


return (
<form className="max-w-sm mx-auto grid gap-3" onSubmit={async (e) => {
e.preventDefault();
try {
await login(username, password);
router.push("/orders");
} catch (e: any) {
setErr(e?.response?.data?.detail || "Login failed");
}
}}>
<h1 className="text-xl font-semibold mb-2">Login</h1>
{err && <div className="text-red-600 text-sm">{err}</div>}
<input className="border p-2 rounded" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
<input className="border p-2 rounded" type="password" placeholder="Password" value={password} onChange={e=>setP(e.target.value)} />
<button className="border rounded p-2">Sign in</button>
</form>
);
}