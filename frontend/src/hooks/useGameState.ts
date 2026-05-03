import { useCallback, useState } from "react";

import { createInitialState, makeChoice, rollDice } from "../game/gameLogic";
import type { ChoiceType, GameState } from "../game/types";

export function useGameState() {
  const [state, setState] = useState<GameState>(() => createInitialState());

  const rollLocalDice = useCallback(() => {
    setState((current) => rollDice(current));
  }, []);

  const makeLocalChoice = useCallback((choice: ChoiceType) => {
    setState((current) => makeChoice(current, choice));
  }, []);

  const resetGame = useCallback(() => {
    setState(createInitialState());
  }, []);

  return {
    state,
    setState,
    rollLocalDice,
    makeLocalChoice,
    resetGame
  };
}
