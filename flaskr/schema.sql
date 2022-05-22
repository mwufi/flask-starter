drop table if exists user;
drop table if exists post;

create table user (
    id integer primary key autoincrement,
    username text unique not null,
    password text not null
);

create table post (
    id integer primary key autoincrement,
    author_id integer not null,
    created timestamp not null default current_timestamp,
    title text not null,
    body text not null,
    foreign key (author_id) references user (id)
);