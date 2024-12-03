"use client";
import { useState, useEffect } from "react";
import io from "socket.io-client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const socket = io("http://localhost:5000"); // Backend WebSocket URL
const n = 5;

export default function Home() {
  const [board, setBoard] = useState(Array(n).fill(Array(n).fill(-1)));
  const [movements, setMovements] = useState(0);
  const [executionTime, setExecutionTime] = useState(0);
  const [memoryUsed, setMemoryUsed] = useState("");
  const [generatedNodes, setGeneratedNodes] = useState(0);
  const [visitedNodes, setVisitedNodes] = useState(0);
  const [isFinished, setIsFinished] = useState(false); // Tracks algorithm status

  useEffect(() => {
    socket.on("update_board", (data) => {
      setBoard(data.board);
    });

    socket.on("update_nodes", (data) => {
      setGeneratedNodes(data.generated_nodes);
      setVisitedNodes(data.visited_nodes);
    });

    socket.on("update_time", (data) => {
      setExecutionTime(data.execution_time);
      setIsFinished(true); // Mark as finished
    });

    socket.on("update_memory", (data) => {
      setMemoryUsed(data.memory_used);
    });

    // Cleanup on unmount
    return () => {
      socket.off("update_board");
      socket.off("update_time");
      socket.off("update_memory");
      socket.off("update_nodes");
    };
  }, []);

  const initHC = async () => {
    setIsFinished(false);
    setGeneratedNodes(0);
    setVisitedNodes(0);
    socket.emit("start");
  }

  return (
      <Card style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <CardHeader>
          <CardTitle>Passeio do Cavalo usando busca em profundidade limitada</CardTitle>
        </CardHeader>
        <CardContent className="justify-between items-center">
            <div style={{
            display: "grid",
            gridTemplateColumns: `repeat(5, 50px)`,
            gap: "2px",
          }}>
            {board.flat().map((value, idx) => (
              <div
                key={idx}
                style={{
                  width: "50px",
                  height: "50px",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  backgroundColor: value === -1 ? "#ddd" : "#4caf50",
                  color: "#fff",
                  fontWeight: "bold",
                  border: "1px solid #ccc",
                }}
              >
                {value !== -1 ? value : ""}
              </div>
            ))}
          </div>
          <Button onClick={initHC} className="mt-10">Iniciar algoritmo</Button>
        </CardContent>
        <CardFooter>
          {isFinished ? (
            <>
              Tempo de execução: {executionTime} <br />
              Memória utilizada: {memoryUsed} <br />
              Número de nós gerados: {generatedNodes} <br />
              Número de nós visitados: {visitedNodes} <br />
            </>
          ) : (
            <>Aguardando execução do algoritmo...</>
          )}
        </CardFooter>
      </Card>
  );
}
