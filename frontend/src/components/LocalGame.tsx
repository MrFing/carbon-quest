import { useNavigate } from "react-router-dom";

import GameBoard from "./GameBoard";
import { useGameState } from "../hooks/useGameState";

export default function LocalGame() {
  const navigate = useNavigate();
  const { state, rollLocalDice, makeLocalChoice, resetGame } = useGameState();

  return (
    <GameBoard
      state={state}
      canPlay={!state.gameOver}
      onRoll={rollLocalDice}
      onChoice={makeLocalChoice}
      onPlayAgain={resetGame}
      onQuit={() => navigate("/")}
    />
  );
}
