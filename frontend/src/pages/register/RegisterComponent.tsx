import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link } from "react-router-dom";

interface RegisterComponentProps {
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function RegisterComponent({ handleSubmit, handleChange }: RegisterComponentProps) {
  return (
    <div className="w-full h-screen flex items-center justify-center bg-secondary">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Create an account</CardTitle>
          <CardDescription>
            Enter your email and password to get started
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <CardContent>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  name="email"
                  onChange={handleChange}
                  placeholder="m@example.com"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  name="password"
                  onChange={handleChange}
                  required
                  minLength={6}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  name="confirmPassword"
                  onChange={handleChange}
                  required
                  minLength={6}
                />
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex-col gap-4">
            <Button type="submit" className="w-full">
              Create Account
            </Button>
            <Button variant="outline" className="w-full" type="button">
              Sign up with Google
            </Button>
            <div className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link to="/login" className="underline underline-offset-4 hover:text-primary">
                Sign in
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

