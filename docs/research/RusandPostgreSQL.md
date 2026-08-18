---
document_id: "research:source:rust-web-services-axum-sqlx-postgresql"
kind: "research"
title: "Architecting and building medium-sized web services in Rust with Axum, SQLx and PostgreSQL"
status: "active"
authority: "repository"
source: "https://kerkour.com/rust-web-services-axum-sqlx-postgresql"
created: "2026-08-18"
updated: "2026-08-18"
supersedes: null
---

> Research source. The runtime preference distilled from this material lives in [`apply-architecture-playbook` entry 001](../../skills/apply-architecture-playbook/references/001-rust-postgres-layered-monolith.md).

While Rust is not as productive as Go and its legendary standard library to write backend services, Rust's rich type system, compiler-enforced correctness and zero-cost abstraction make it a great choice nonetheless, especially for medium-sized services (10K+ lines of code and 100 or so endpoints) if you want to spend less time fixing business logic bugs or need high performance. No more null pointer dereference or fields forgotten when creating a `struct`, and of course, there is no going back once you have tasted enums.

Over the years, I've developed a few patterns to quickly build such medium-sized services and that's what I'm sharing with you today.

See *[Rust service hardening and production checklist](/rust-service-hardening-and-production-checklist)* for how to deploy Rust services.

## Rust's HTTP ecosystem

First, let's see how the many different crates that you need to run an HTTP server fit together.

![Rust HTTP stack](https://kerkour.com/assets/2024/06/rust_http_ecosystem.avif)

At the bottom of the stack you can find the async runtime (what is a runtime? [Take a look here](/rust-async-await-what-is-a-runtime)): `tokio`. The runtime is reponsible for [scheduling the different tasks](/rust-vs-go-concurrency-models-stackfull-vs-stackless-coroutines) and providing an async version of the Operating System's sockets API. Here, `tokio` listen and accept new TCP connections.

Then comes the [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) layer, in charge of securing the traffic that is sent and received.

This layer is actually composed of 2 parts: `tokio_*` (such as `tokio_rustls` or `tokio_boring`) and a few libraries implementing the TLS protocol.

There are a few crates available to handle the TLS protocol: `rustls`, `boring` and `openssl`. I recommend to use `rustls` because it's a Rust-native library, so it's statically linked to your executables and you will encounter less problem when deploying your servers (does the server's VM/Docker image contains the correct version of OpenSSL...) or when trying to cross-compile your programs.

The `tokio_rustls` crate wraps `tokio` types and `rustls` types into an unified layer. Concretely, it turns a `tokio` 's [`TcpStream`](https://docs.rs/tokio/latest/tokio/net/struct.TcpStream.html) into a [`TlsStream`](https://docs.rs/tokio-rustls/latest/tokio_rustls/server/struct.TlsStream.html) that handles data encryption and decryption. Each TLS library has its equivalent `tokio_` crate, such as [tokio\_boring](https://docs.rs/tokio-boring/latest/tokio_boring/).

Once you have your TLS stream, you need to pipe it into [`hyper`](https://github.com/hyperium/hyper). `hyper` is the brain of the whole stack. It turns bytes from the network into [`Request`](https://docs.rs/hyper/latest/hyper/struct.Request.html) and [`Response`](https://docs.rs/hyper/latest/hyper/struct.Response.html) structures. Hyper is transport agnostic, it just turns streams of bytes into structured requests and responses.

In pseudo code:

```
let server_tls_config = rustls::ServerConfig::builder(); // ...
let tls_acceptor = tokio_rustls::TlsAcceptor::from(Arc::new(server_tls_config));

let listener = tokio::net::TcpListener::bind(SocketAddr::from(([127, 0, 0, 1], 8080))).await?;

loop {
    let (stream, remote_socket_addr) = listener.accept().await?;
    let tls_acceptor = tls_acceptor.clone();

    let request_handler = hyper::service::service_fn(move |mut req| {
        let remote_socket_addr = remote_socket_addr.to_string();
        req.extensions_mut().insert(socket_addr_str);
        actual_handler(req)
    });

    tokio::spawn(async move {
        let tls_stream = tls_acceptor.accept(stream).await.unwrap(); // need to handle error
        if let Err(err) = hyper_util::server::conn::auto::Builder::new(TokioExecutor::new())
            .serve_connection_with_upgrades(TokioIo::new(tls_stream), request_handler)
            .await
        {
            error!("failed to serve connection: {err:#}");
        }
    })
}
```

For that, it relies on "codecs" that decode the actual bytes from the network depending the different versions of the HTTP protocol: `http` for HTTP/1.X, `h2` for HTTP/2.X and so on.

On top of `hyper`, there is [`axum`](https://github.com/tokio-rs/axum), the ergonomic layer providing utilities that programmers are expecting when developing web servers: a [router](https://docs.rs/axum/latest/axum/struct.Router.html), [middlewares](https://docs.rs/axum/latest/axum/middleware/index.html), [error handling](https://docs.rs/axum/latest/axum/error_handling/index.html). ["extractors"](https://docs.rs/axum/latest/axum/extract/index.html) and more.

On the client-side, [`reqwest`](https://github.com/seanmonstar/reqwest) is the equivalent of `axum` and provides connection pooling, proxy handling, hostname resolution and more.

Then there is a myriad of crates such as `tower` which tries to bring unified handlers and middlewares to the Rust HTTP ecosystem with its [`Service`](https://docs.rs/tower/latest/tower/trait.Service.html) and [`Layer`](https://docs.rs/tower/latest/tower/trait.Layer.html) trait.

Finally, the (maybe) most important piece of the puzzle: observability. In Rust, the community has converged around [`tracing`](https://docs.rs/tracing/latest/tracing/) which is (again) maintained by the tokio team and provides utilities to handle all your structured logging and tracing needs.

## Code organization

The code is organized in layers:

- The HTTP / scheduler / worker layer which handles the requests, triggers and cron jobs of the service.
- The service layer, where all the business logic lives, with a `model.rs` file for constants and types.
- The repository layer which wraps database calls.

![Server's architecture](https://kerkour.com/assets/2022/web-application-architecture/ch10_webapp_architecture.avif)

As far as I know, this architecture has no official and shiny name, but I have used it with success for projects exceeding tens of thousands of lines of code in Rust, Go, and Node.JS.

The advantage of using such architecture is that, if in the future the requirements or one dependency are revamped, changes are locals and isolated.

Each layer can only communicate with the layer directly above or below e.g. the HTTP layer can't call a method on a repository.

```
\$ ls
my-server/
    migrations/
        0001.sql
    Cargo.toml
    main.rs
    server.rs
    scheduler.rs
    worker.rs
    webapp.rs
libs/
    mailer/
        Cargo.toml
        mailer.rs
    queue/
        Cargo.toml
        queue.rs
    stripe/
        Cargo.toml
        stripe.rs
services/
    users/
        repository/
            users.rs
            sessions.rs
        service/
            get_user.rs
            get_session.rs
        Cargo.toml
        errors.rs
        model.rs
        repository.rs
        service.rs
Cargo.toml <- Cargo.toml for the workspace
Dockerfile.my-server
Makefile
README.md
```

I think that the tree above speaks for itself, but if you want more details, take a look at my article *[How to organize large Rust codebases](/rust-how-to-organize-large-workspaces)*.

There is usually 1 `Dockerfile` per cmd.

## HTTP layer

The HTTP layer is straightforward: it turns HTTP requests into structures to be used by the service layer and vice versa.

Rust's HTTP ecosystem being rather instable, this thin layer enables us to be able to change our HTTP framework with very little efforts if the need comes.

```
pub fn new_api_router(server_state: Arc<ServerState>) -> Router {
    let router = Router::new()
        .route("/user/{user_id}", get(get_user))
        .with_state(server_state);

    return router;
}

// ctx contains various information about the request such as the client's IP address
pub async fn get_user(
    Extension(ctx): Extension<RequestContext>,
    State(api_state): State<Arc<ServerState>>,
    Path(user_id): Path<String>,
) -> Result<Json<User>, errs::Error> {
    let user = api_state.users.get_user(ctx, GetUserInput { id: user_id }).await?;
    return Ok(Json(user));
}
```

## Services

The service layer contains all the business logic of the service: authentication, data validation, business invariants...

**users\_service.rs**

```
pub struct UsersService {
    pub repo: UsersRepository,
    pub db: pg::Pool,
    pub queue: Arc<Queue>,
    pub mailer: Arc<dyn Mailer>,
    // ...
}

impl UsersService {
    pub fn new(
        repo: UsersRepository,
        config: &'static config::Config,
        db: pg::Pool,
        queue: Arc<Queue>,
        mailer: Arc<dyn Mailer>,
    ) -> UsersService {
        return UsersService {
            repo,
            db,
            queue,
            mailer,
            // ...
        };
    }
}
```

**get\_user.rs**

```
impl UsersService {
    pub async fn get_user(&self, ctx: RequestContext, input: GetUserInput) -> Result<User, Error> {
        // auth_checks, input validation...

        let user = self
            .repo
            .find_user_by_id(&self.db, input.id)
            .await?;
        return Ok(user);
    }
}
```

## Repositories

Repositories' only purpose is to encapsulate database queries (and NOT to use both MongoDB and Postgres as the database and other fantasies).

Why not implement queries directly in the services' methods?

First, because you may want to reuse a query in different service methods e.g `SELECT * FROM users`.

But also because when you have all you queries related to a table in a single file, it's way easier to add and remove columns to/from your queries.

**services/users/repository.rs**

```
pub struct UsersRepository {}

impl UsersRepository {
    pub fn new() -> Self {
        return UsersRepository {};
    }
}
```

**services/users/repository/users.rs**

```
/// 'c is the lifetime of the underlying database connection
pub trait Queryer<'c>: Executor<'c, Database = sqlx::Postgres> {}

impl<'c> Queryer<'c> for &Pool {}
impl<'c> Queryer<'c> for &'c mut PgConnection {}

impl UsersRepository {
    #[instrument(skip_all)]
    pub async fn create_user<'c, Q: pg::Queryer<'c>>(&self, db: Q, user: &User) -> Result<(), Error> {
        const QUERY: &str = "INSERT INTO users (id, email)
            VALUES (\$1, \$2)";

        sqlx::query(QUERY)
            .bind(user.id)
            .bind(&user.email)
            .execute(db)
            .await
            .map_err(|err| match err {
                sqlx::Error::Database(db_err) if db_err.constraint().is_some() => Error::EmailAlreadyInUse,
                err => Error::Unspecified(format!("users.create_user: {err}")),
            })?;

        return Ok(());
    }

    // update_user
    // delete_user
    // ....
}
```

## Background jobs (queue)

I've already covered how to build a job queue with Rust and Postgres in [How to build a job queue with Rust and PostgreSQL](/rust-job-queue-with-postgresql) and nothing has changed since then.

> Want to learn real-world Rust, security engineering and applied cryptography? Take a look at my book [Black Hat Rust](/black-hat-rust), where, from theory to practice, you will learn how to build crawlers, an end-to-end encrypted Remote Access Tool and exploits in Rust, and many other things to get your hands dirty.

## Cron jobs

Cron jobs are a little bit trickier to handle than the background jobs (but not much, don't worry) because you want to have multiple replicas of your service for high-availability, and thus you need to elect a leader to avoid having 10 cron schedulers firing 10 times the same task at the same time.

Once again, Postgres got our back covered, so take a look at my article *[Leader election with PostgreSQL's advisory locks](/postgresql-leader-election-advisory-lock)* to learn how to implement simple yet extremely robust leader election with Postgres.

**scheduler.rs**

```
pub async fn run(mut shutdown: watch::Receiver<bool>, queue: Arc<Queue>,) -> Result<(), Error> {
    let scheduler = Scheduler::new();

    let _leader_conn = tokio::select! {
        _ = shutdown.changed() => {
            info!("scheduler: Stopping");
            return Ok(());
        }
        leader_conn = pg::try_to_become_leader(db, pg::SCHEDULER_LEADER_LOCK_ID) => {
            match leader_conn? {
                Some(conn) => conn,
                // the advisory lock couldn't get acquired in time so we exit.
                None => return Ok(()),
            }
        }
    };

    info!("scheduler: is leader");

    // every hour at xx:00
    scheduler.add_job("0 0 * * * *",  move || {
        Box::pin(async {
            users::users_related_task(queue).await;
            Ok(())
        })
    }).await;

    let scheduler_handle = scheduler.run().await
        .map_err(|err| Error::Internal(format!("scheduler: error starting scheduler: {err}")))?;

    info!("scheduler: Starting");

    tokio::select! {
        _ = scheduler_handle => {},
        _ = shutdown.changed() => {
            info!("scheduler: Stopping");
        },
    };

    info!("scheduler: Stopped");

    Ok(())
}
```

## Caching

Caching data reduces the number of expensive database and API calls and makes systems snappier.

Caching is done exclusively at the service layer. Remember, the repository layer must stay dumb, so no caching here. Also, caching often depends on business rules (e.g it's safe to cache this entity for only 1 hour), thus it should be done at the service layer.

A general-purpose library like [moka](https://github.com/moka-rs/moka) is enough for most use cases.

## Logging

The [tracing](https://github.com/tokio-rs/tracing) crate got your back covered for both simple and structured logging.

## Serving Single Page Applications and static assets

These medium-sized web services are often accompanied by a Single Page Application (SPA) built with React or VueJS and some static assets (images, CSS stylesheets...).

I prefer to serve those directly from the same server as the API (instead of a static CDN such as [Cloudflare Pages](/cloudflare-for-speed-and-security)).

First because it greatly simplifies the deployment of the service, but also because serving web applications on the same domain as the API lets you avoid the ["CORS tax"](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS).

Who could have guessed that simple systems are actually faster?

For that, I use the [rust-embed](http://crates.io/crates/rust-embed) crate and build a custom `axum` handler:

**webapp.rs**

```
#[derive(Embed)]
#[folder = "./webapp"]
struct Assets;

pub async fn webapp_handler(uri: Uri) -> Response {
    let path = clean_path(uri.path());

    match Assets::get(path) {
        Some(file) => serve_file(path, file),
        None => serve_index_html(not_found_status_code),
    }
}
```

**routers.rs**

```
let webapp_and_api_router = Router::new()
    .nest("/api", api_routes)
    .fallback(webapp::webapp_handler);
```

## Some Closing Thoughts

Aristotle once said: *"Using Rust is the beginning of all wisdom"*.

Or maybe he didn't say that, I'm not sure what is real or not these days... Anyway, I actually have nothing to add. Rust has been a great asset for building reliable web services that are easy to maintain over a long period of time. Don't [overthink](/overthinking) and just give it a try instead of planning 10 meetings and 3 months of research to see if it's a great fit for your 20 endpoints service 🦞

Now, if you want to learn embedded development, take a look at [Introduction to embedded development with Rust: Overview of the ecosystem](/introduction-to-embedded-development-with-rust).

If you want to learn applied cryptography, start with [Cryptographic Right Answers: Post Quantum and Rust Edition](/post-quantum-cryptography-recommendations-rust).

Finally, if you want to learn from years of experience of software and security engineering, take a look at my books:

- [Blak Hat Rust](https://kerkour.com/black-hat-rust), where, from theory to practice, you will learn Rust, security engineering and applied cryptography, and build many projects such as multiple crawlers, an end-to-end encrypted Remote Access Tool (RAT), an evil-twin phishing access point, build shellcodes in Rust with `#![no_std]` instead of assembly and many more things to get your hands dirty.
- [Continuous Learning](https://kerkour.com/continuous-learning) where I share everything I've learned about learning to learn, which is the most important skill for any white collar evolving in a fast-changing world. Based on neuroscience, I've built a simple system that enables me to accumulate knowledge and use it to my advantage in the information age.

100% LLM-free and DRM-free, of course.
