import type { NextApiRequest, NextApiResponse } from 'next';
import clientPromise from '../../lib/mongodb';
import bcrypt from 'bcryptjs';
import Realm from 'realm';


type Data = {
  message: string;
  userId?: string;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse<Data>) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ message: 'Username, email, and password are required' });
  }

  try {
    const client = await clientPromise;
    const db = client.db('account_info');

    // Check if the email or username already exists
    const existingUser = await db.collection("user_info").findOne({ $or: [{"email": email}, {"username": username}] });
    if (existingUser) {
      if (existingUser.email === email) {
        return res.status(409).json({ message: 'Email already exists' });
      }
      if (existingUser.username === username) {
        return res.status(409).json({ message: 'Username already exists' });
      }
    }

    if (password.length < 6) {
      return res.status(409).json({message: 'Password is too short'});
    }
    if (password.length > 128) {
      return res.status(409).json({message: 'Password is too long'});
    }

    // Hash the password before storing
    //const hashedPassword = await bcrypt.hash(password, 10);
    const hashedPassword = password;

    const app = new Realm.App({
      id: "data-vkrre"
    })
    await app.emailPasswordAuth.registerUser({
      email: email,
      password: hashedPassword,
    });

    // Insert the new user
    const result = await db.collection("user_info").insertOne({ username, email, password: hashedPassword, saveSearchHist: true, "logins": 1 });

    return res.status(201).json({ message: 'User created', userId: result.insertedId.toString() });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
