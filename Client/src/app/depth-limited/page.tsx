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
  const [movements, setMovements] = useState("");

  useEffect(() => {
    // Listen for board updates from the backend
    socket.on("update_board", (data) => {
      setBoard(data.board);
      setMovements(data.movements);
    });

    // Cleanup on unmount
    return () => socket.off("update_board");
  }, []);

  useEffect(() => {
    socket.on("update_movements", (data) => {
      setMovements(data.movements);
    });

    return () => socket.off("update_movements");
  }, []);

  const initHC = async () => {
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
          Movimentos: {movements}
        </CardFooter>
      </Card>
  );
}
