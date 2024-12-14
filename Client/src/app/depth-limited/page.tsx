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
import { useRouter } from "next/navigation";

const socket = io("http://localhost:5000"); // Conexão estabelecida via WebSocket
const n = 5; // Valor de N, por padrão 5

export default function Home() {
  const [inputN, setInputN] = useState(5);
  const [n, setN] = useState(5);
  const [board, setBoard] = useState(Array(n).fill(Array(n).fill(-1)));
  const [executionTime, setExecutionTime] = useState(0);
  const [memoryUsed, setMemoryUsed] = useState(0);
  const [generatedNodes, setGeneratedNodes] = useState(0);
  const [visitedNodes, setVisitedNodes] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [isPossible, setIsPossible] = useState(false);
  const [lin, setLin] = useState(0);
  const [col, setCol] = useState(0);
  const [timeLimitExceed, setTimeLimitExceed] = useState(false);

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
    });

    socket.on("update_memory", (data) => {
      setMemoryUsed(data.memory_used);
    });

    socket.on("execution_finished", (data) => {
      setIsPossible(data.possible);
      setIsFinished(true);
      setTimeLimitExceed(data.tle);
    })

    return () => {
      socket.off("update_board");
      socket.off("update_time");
      socket.off("update_memory");
      socket.off("update_nodes");
    };
  }, []);

  const handleGridSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSize = parseInt(event.target.value, 10);
    if (!isNaN(newSize) && newSize > 0) {
      setInputN(newSize);
    }
  };
  
  const handleLineChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSize = parseInt(event.target.value, 10);
    if (!isNaN(newSize) && newSize > 0) {
      setLin(newSize);
    }
  };

  const handleColumnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newSize = parseInt(event.target.value, 10);
    if (!isNaN(newSize) && newSize > 0) {
      setCol(newSize);
    }
  };

  const applyGridSize = () => {
    setN(inputN);
    setLin(lin);
    setCol(col);
    setBoard(Array(inputN).fill(Array(inputN).fill(-1)));
    setIsFinished(false);
  };

  const initDLS = async () => {
    setIsFinished(false);
    setGeneratedNodes(0);
    setVisitedNodes(0);
    setTimeLimitExceed(false);
    socket.emit("start", {n, lin, col, alg: "DLS"});
  };

  const router = useRouter();
  const redirectToHome = () => {
    router.push('/');
  };

  return (
      <Card style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <CardHeader>
          <CardTitle>Passeio do Cavalo usando busca em profundidade limitada</CardTitle>
        </CardHeader>
        <CardContent className="justify-between items-center">
        <div style={{ marginBottom: "20px" }}>
          <label htmlFor="grid-size">Tamanho do tabuleiro (N): </label>
          <input
            id="grid-size"
            type="number"
            value={inputN}
            onChange={handleGridSizeChange}
            style={{
              width: "50px",
              textAlign: "center",
              marginLeft: "10px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              padding: "5px",
            }}
          />
          <label htmlFor="grid-size" className="ml-10">Posição Inicial: </label>
          <input
            id="grid-size"
            type="number"
            value={lin}
            onChange={handleLineChange}
            style={{
              width: "50px",
              textAlign: "center",
              marginLeft: "10px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              padding: "5px",
            }}
          />
          <input
            id="grid-size"
            type="number"
            value={col}
            onChange={handleColumnChange}
            style={{
              width: "50px",
              textAlign: "center",
              marginLeft: "10px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              padding: "5px",
            }}
          />
        </div>
        
        <div style={{display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "20px",
          }}
        >
          <Button onClick={applyGridSize} style={{ marginBottom: "20px", textAlign: "center" }}>Confirmar</Button>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `repeat(${n}, 50px)`,
              gap: "2px",
            }}
          >
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
          <Button onClick={initDLS} className="mt-10" style={{ marginTop: "20px", textAlign: "center" }}>Iniciar algoritmo</Button>
        </div>
        </CardContent>
        <CardFooter style={{display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: "20px"}}>
          {isFinished ? (
            <>
              {timeLimitExceed ? "Tempo limite extrapolado!" : 
              !isPossible ? `Não foi encontrada uma solução para o tamanho ${n}`: "Solução obtida com sucesso"} <br />
              Tempo de execução: {executionTime} segundos <br />
              Memória utilizada: {memoryUsed} MB <br />
              Número de nós gerados: {generatedNodes} <br />
              Número de nós visitados: {visitedNodes} <br />
            </>
          ) : (
            <>Aguardando execução do algoritmo...</>
          )}
          <Button onClick={redirectToHome} className="mt-10">Voltar</Button>
        </CardFooter>
      </Card>
  );
}
