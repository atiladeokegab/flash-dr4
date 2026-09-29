# Pitch: Shop Assistant in 60 seconds

**The problem.** Six laptops means six spec sheets. Shoppers don't want to compare weights,
battery hours and prices line by line. They want to ask "which is best for travel under
£900?" and get one clear answer with a reason.

**What Shop Assistant does.** It's a product page with a chat panel. Ask in plain words and
the assistant answers in a sentence, and the laptops it recommends light up in the grid.
Ask a follow-up and the highlights move. It only answers from the page's own catalog: the
server drops any product that isn't on sale here, so it can't invent one. Bad input is
refused, and if the AI fails the page says so instead of guessing.

**The stack.** A FastAPI backend with two endpoints. Claude Haiku 4.5
does the answering, with an offline stub as a fallback. The front end is a single vanilla
web page: no framework.

**Shop Assistant: ask a question, get one clear answer.**
