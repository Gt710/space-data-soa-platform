package com.spacedata

import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import java.io.File
import java.util.*

// Опис таблиці для супутників
object Satellites : Table("satellites") {
    val id = integer("id").autoIncrement()
    val name = varchar("name", 100)
    val noradId = integer("norad_id").uniqueIndex()
    val launchDate = varchar("launch_date", 20)

    override val primaryKey = PrimaryKey(id)
}

fun main() {
    // Підключення до БД
    Database.connect(
        url = "jdbc:postgresql://localhost:5432/spacedata",
        driver = "org.postgresql.Driver",
        user = "admin",
        password = "admin_pass"
    )

    // Створення таблиць
    transaction {
        SchemaUtils.create(Satellites)
    }

    embeddedServer(Netty, port = 8080, host = "0.0.0.0", module = Application::module)
        .start(wait = true)
}

fun Application.module() {
    install(ContentNegotiation) {
        json()
    }
    
    routing {
        get("/") {
            call.respond(mapOf("service" to "satellite-tracker", "status" to "online"))
        }
        
        get("/satellites") {
            val result = transaction {
                Satellites.selectAll().map {
                    mapOf(
                        "name" to it[Satellites.name],
                        "norad_id" to it[Satellites.noradId],
                        "launch_date" to it[Satellites.launchDate]
                    )
                }
            }
            call.respond(result)
        }

        get("/add-test") {
            transaction {
                Satellites.insert {
                    it[name] = "ISS (ZARYA)"
                    it[noradId] = 25544
                    it[launchDate] = "1998-11-20"
                }
            }
            call.respond(mapOf("status" to "Added ISS to DB"))
        }
    }
}
