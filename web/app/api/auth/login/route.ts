import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST(request: Request) {
  const { email, password, passcode } = await request.json();

  const validEmail = process.env.AUTH_EMAIL;
  const validPassword = process.env.AUTH_PASSWORD;
  const validPasscode = process.env.AUTH_PASSCODE;

  if (!validEmail || !validPassword || !validPasscode) {
    return NextResponse.json(
      { error: "Auth not configured" },
      { status: 500 }
    );
  }

  if (
    email !== validEmail ||
    password !== validPassword ||
    passcode !== validPasscode
  ) {
    return NextResponse.json(
      { error: "Invalid email, password, or passcode" },
      { status: 401 }
    );
  }

  // Create a simple session token (hash of credentials + timestamp)
  const token = Buffer.from(
    `${validEmail}:${Date.now()}:${crypto.randomUUID()}`
  ).toString("base64");

  const cookieStore = await cookies();
  cookieStore.set("gl-session", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24, // 24 hours
  });

  return NextResponse.json({ ok: true });
}
