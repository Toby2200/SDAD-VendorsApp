## [1]. <Backend language and framework choice>
Date: 2026-09-26
Status: Decided
Context: I need to build a small-medium project with an SQLite database where we have read/write. The stack should be for rapid development, and ready for feature division.
Decision: The stack that will be used for this project is python as the programming langauge, due to the fact that is really commmon, and is the one in which we have more experience in classes. Then Flask as the microframework since it gives a lot of freedom to organize the project in blueprint without adding extra things. SQLite for the database.
Alternatives considered: Django can work great for a really big project, but may be overengineering for this one. It work really good, the problem is that it adds an extra step nto blueprint creations, and is not as flexible. 
Consequences: The project will be really light, and structured with its dependencies. But this project needs to be organized in order to have the two feature working almost independent. 


## [2]. <How you scoped your two feature domains to be independently modularizable>
Date: 2026-09-26
Status: Decided
Context: The system needs at least two independent features, where they could work together. But the domains can interact through clearly defined interfaces without depending on each other's internal implementation. In order to achieve this we need to consider how we are going to organize the project, and how each feature is connected with the database.
Decision: I chose that the project will be organized by feature, so each feature will have its own folder. One will have the funtionality of the catalog and stock, and the other one will be to manage the orders. Each of them will have its own routes, models, flask blueprints, and business logic.
Alternatives considered: Another alternative that we had was to organized the project by layers, where we organize the code depending on what it does, not its business logic. Like all routes togther, all database models together. But this is mixing the two features.
Consequences: Dividing the project into package by feature establishes clear boundries between each feature, which makes easy to unit test each module. The tradeoff is that we could have some code duplication between each module.


## [3]. <A data-model/schema decision in SQLite>
Date: 2026-09-28
Status: Decided
Context: We need to define the schema for clearance and persistance inside the users (vendors) table, for catalog table, and sales tables. The system should enforce relational integrity, while having a legal picture of the orders, ensuring that historical records remain immutable even if a product changes.
Decision: I am going to use a relational database with SQLite to model the vendors and clients orders and catalog visibility. I decided that the table orderDetails is going to have not only the Foreign Key of  'id_product', but due to store historical snapshots we are going to have also the product information such as: 'code', 'description', and 'unit_price' at the moment of the sale.
Alternatives considered: An alternative that I had was to use only the Foreign Key of the product in the orderDetails, but if the product changes its price or something else, there would not be a legal picture of what was really sold.
Consequences: Now we have a good approach of relational data, and wrting or retrieveng. The only trade-off is that we are going to have some duplication of data inside the orderDetails.

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


## [4]. <Your testing approach>
Date: 2026-10-04
Status: Decided
Context: To state that the program works good, is not only that the happy path works. We need to test each part, we could do unit testing, integration, and E2E. To measure the amount of coverage we have in testing is from all the lines we have how many are running when we test? And for this specific projetc we need at least 70% tested code. 
Decision: The decision I made was to have a temporary database only for the testing and for each test we have the template. Then the service funtions are easy to try, since we know the parameters, and the returns, so we only need to cll them and assert. And for the routes (APIs) what I did was to create a simulation of a client or running aplication and call each route individualy passing some of the arguments that it needs. So I prioritized all /service.py and tryied to have all the /routes.py, what I could not prioritize was rase value of change == 0, because we cant try that, breaking the database, or making change in it while using the app. 
Alternatives considered: For testing there are many alternative ways to do each thing, for instance if we want the routes to be unit test instead of integration testing we could mock them. So we could mock the entire process (input, functions, output) and we do not need to run an API call. And another alternative that I had was to use the real database to try the project.
Consequences: The consecuences of choosing which alternative to use, is if you want to also check states, or cookies probably is a good idea to use a client. But if you want to only try the functionality, and know wheres the exact location of the error it is a better option to use 100% mocking. The reason we did not use the real db was because it was dynamic, so each try we tested the program the assertions where giving different results. While having a template db makes the answers always teh same. 


## [5]. <One thing you deliberately chose not to build>
Date: 2026-10-04
Status: Decided
Context: When I planed this aplication in the planing stage, I was thinking of what features I could add. Obvously I thought of many ideas which could work great for this project.
Decision: I thought of making a vector database within the products description. So we could recomend people similar object to the ones they are looking for. Since I was trying to create the whole project by my self, almost without AI copy/paste, so it was difficult to advance a lot in one day. And this was the first class where we needed to create APIs or do something else than just algorithms in python. 
Alternatives considered: What we are doing right now is when searching for a product we just show products with same letters as the one the vendor (client) is searching.
Consequences: The application is running good y a happy path, but I think if this was a real aplication it will give a lot profit to the business to have the vector database for recomendation. Due to the fact that if they get out of stock of one specific products, but they have a really similar one. They could sell the that is really similar instead of loosing the order.