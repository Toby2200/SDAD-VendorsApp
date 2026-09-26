## [1]. <Backend language and framework choice>
Date: 2026-09-26
Status: Decided
Context: I need to build a small-medium project with an SQLite database where we have read/write. The stack should be for rapid development, and ready for microservices division.
Decision: The stack that will be used for this project is python as the programming langauge, due to the fact that is really commmon, and is the one in which we have more experience in classes. Then Flask as the microframework since it gives a lot of freedom to organize the project in blueprint without adding extra things. SQLite for the database.
Alternatives considered: Django can work great for a really big project, but may be overengineering for this one. It work really good, the problem is that it adds an extra step nto blueprint creations, and is not as flexible. 
Consequences: The project will be really light, and structured with its dependencies. But this project needs to be organized in order to have the two microservices working almost independent. 
