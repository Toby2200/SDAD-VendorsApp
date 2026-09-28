## [1]. <Backend language and framework choice>
Date: 2026-09-26
Status: Decided
Context: I need to build a small-medium project with an SQLite database where we have read/write. The stack should be for rapid development, and ready for microservices division.
Decision: The stack that will be used for this project is python as the programming langauge, due to the fact that is really commmon, and is the one in which we have more experience in classes. Then Flask as the microframework since it gives a lot of freedom to organize the project in blueprint without adding extra things. SQLite for the database.
Alternatives considered: Django can work great for a really big project, but may be overengineering for this one. It work really good, the problem is that it adds an extra step nto blueprint creations, and is not as flexible. 
Consequences: The project will be really light, and structured with its dependencies. But this project needs to be organized in order to have the two microservices working almost independent. 


## [2]. <How you scoped your two feature domains to be independently modularizable>
Date: 2026-09-26
Status: Decided
Context: The system needs at least two independent features, where they could work together. But the domains can interact through clearly defined interfaces without depending on each other's internal implementation. In order to achieve this we need to consider how we are going to organize the project, and how each feature is connected with the database.
Decision: I chose that the project will be organized by feature, so each feature will have its own folder. One will have the funtionality of the catalog and stock, and the other one will be to manage the orders. Each of them will have its own routes, database models, flask blueprints, and business logic.
Alternatives considered: Another alternative that we had was to organized the project by layers, where we organize the code depending on what it does, not its business logic. Like all routes togther, all database models together. But this is mixing the two features.
Consequences: 1-2 sentences, what this costs or enables later. Dividing the project into package by feature establishes clear boundries between each microservice, which makes easy to unit test each module. The tradeoff is that we could have some code duplication between each module.


## [3]. <A data-model/schema decision in SQLite>
Date: 2026-09-28
Status: Decided
Context: 1-3 sentences, what forced this decision
Decision: 1-2 sentences, what you chose
Alternatives considered: at least one real alternative, and why you rejected it
Consequences: 1-2 sentences, what this costs or enables later

vendors{
    int vendor_id autoincrement, 
    string name,
    string last_name,
    string mail unique,
    string password hash,
    int active
}

clients{
    int client_id autoincrement,
    string name, 
    string ubicacion, 
    string mail, 
    string cedula juridica, 
    int vendor_id
}

products{
    int id_product autocrement,
    string code unique,
    string description,
    int quantity,
    int active, 
    float price
}

orders{
    int id_order autoincrement,
    int vendor_id,
    int client_id, 
    string date
}

orderDetails{
    int id_orderDetail autoincrement,
    int id_order, 
    int id_product, 
    string code, 
    string description,
    int quantity, 
    float unit_price,
    float subtotal
}