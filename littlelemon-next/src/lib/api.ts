import axios from "axios";
import { logout } from "./auth";


export const api = axios.create({
baseURL: process.env.NEXT_PUBLIC_API_URL,
});


let refreshing: Promise<string> | null = null;


api.interceptors.request.use((config) => {
if (typeof window !== "undefined") {
const access = localStorage.getItem("access");
if (access) config.headers.Authorization = `Bearer ${access}`;
}
return config;
});


api.interceptors.response.use(
(r) => r,
async (err) => {
const status = err.response?.status;
const original: any = err.config;
if (status === 401 && !original._retry) {
original._retry = true;
const refresh = typeof window !== "undefined" ? localStorage.getItem("refresh") : null;
if (!refresh) return Promise.reject(err);
if (!refreshing) {
refreshing = api
.post("/auth/jwt/refresh/", { refresh })
.then((res) => {
const token = res.data.access as string;
localStorage.setItem("access", token);
return token;
})
.catch(async (e) => {
await logout();
throw e;
})
.finally(() => {
refreshing = null;
});
}
const token = await refreshing;
original.headers.Authorization = `Bearer ${token}`;
return api.request(original);
}
return Promise.reject(err);
}
);