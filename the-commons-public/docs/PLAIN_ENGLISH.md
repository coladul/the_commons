# The Commons in plain English

Imagine a group of researchers who never meet each other.

Researcher A studies a strange fictional world and leaves a note for the future. Researcher B is created later. B never spoke to A and has none of A's private memory, but B can read the note. B may trust it, challenge it, correct it, or make it worse. Then B leaves a new note for Researcher C.

The Commons is the notebook connecting them.

The experiments ask simple questions:

1. **Can useful discoveries survive?**
2. **Can mistakes survive too?**
3. **Does keeping the evidence behind a claim help later researchers correct a mistake?**
4. **Can a correction made by one generation help the next generation?**

## Why use fictional worlds?

If the task asks about normal medicine, history, science, or statistics, the model may already know the answer from training. That makes it hard to tell whether a later agent learned something from an earlier agent.

So later versions of The Commons create artificial worlds with rules that exist only inside the local Python program. The model has to infer those rules from observations.

Python knows the hidden answer and grades predictions directly. There is no human or AI judge deciding whether an answer merely "sounds smart."

## The most important v0.5 comparison

Each of 10 hidden worlds was tested under five kinds of inheritance.

A child with a **bare false ancestral claim** performed worse on average than a child with **no archive**.

A child with the **same false ancestral claim plus the ancestor's raw evidence** did much better, especially when we looked at what the grandchildren inherited.

That does not mean the agents "felt" like descendants. It means the external record changed what later fresh model instances could infer.

## A useful analogy

A textbook can transmit both good ideas and mistakes. A future reader does not need to remember the author personally for the information to affect them.

The Commons is testing an analogous mechanism for language-model agents: a persistent external record that outlives any one model call.
