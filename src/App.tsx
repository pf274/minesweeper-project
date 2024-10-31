import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { SquareClass, SquareComponent } from "./Square";

import "./App.css";

function generateBoard() {
  const board: SquareClass[][] = [];
  for (let i = 0; i < 9; i++) {
    const newRow = [];
    for (let j = 0; j < 9; j++) {
      const newSquare = new SquareClass({
        isMine: Math.random() < 0.15,
        revealed: true,
        flagged: false,
        position: { x: i, y: j },
        isMineHidden: true,
      });
      newRow.push(newSquare);
    }
    board.push(newRow);
  }
  return board;
}

function App() {
  const [board, setBoard] = useState(generateBoard());

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        {board.map((row, index) => {
          return (
            <div
              key={index}
              style={{
                display: "flex",
                flexDirection: "row",
                flexWrap: "nowrap",
              }}
            >
              {row.map((cell, index) => {
                return (
                  <SquareComponent
                    key={index}
                    size={50}
                    square={cell}
                    board={board}
                  />
                );
              })}
            </div>
          );
        })}
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
