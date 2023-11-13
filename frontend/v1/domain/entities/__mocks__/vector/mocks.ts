import { Vector } from "../../vector/Vector";

export const createVectorMock = (id: string) => {
  return new Vector(id, "NAME", "TITLE", 0);
};
