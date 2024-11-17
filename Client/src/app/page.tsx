"use client";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const redirectToDLSPage = () => {
    router.push(`/depth-limited`);
  };

  const redirectToHCPage = () => {
    router.push(`/hill-climbing`);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Bem-vindo(a)!</CardTitle>
          <CardDescription>Selecione um dos algoritmos de busca abaixo para visualizar a resolução do problema do passeio do cavalo.</CardDescription>
        </CardHeader>
        <CardContent className="justify-between items-center">
          <Button onClick={redirectToDLSPage}>Profundidade limitada</Button>
          <Button onClick={redirectToHCPage} className="mt-5">Subindo o morro</Button>
        </CardContent>
      </Card>
    </main>
  );
}
