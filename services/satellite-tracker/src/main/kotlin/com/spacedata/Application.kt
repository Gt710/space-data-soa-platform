package com.spacedata

import io.ktor.client.*
import io.ktor.client.engine.apache.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.http.HttpMethod
import io.ktor.http.HttpHeaders
import java.util.*
import kotlinx.serialization.Serializable
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction

// Опис таблиці для супутників
object Satellites : Table("satellites") {
    val id = integer("id").autoIncrement()
    val name = varchar("name", 100)
    val noradId = integer("norad_id").uniqueIndex()
    val launchDate = varchar("launch_date", 20)

    override val primaryKey = PrimaryKey(id)
}

@Serializable
data class TleResponse(val status: String, val count: Int, val data: List<SatelliteTle>)

@Serializable
data class SatelliteTle(
        val name: String,
        val norad_id: String,
        val tle_line1: String,
        val tle_line2: String
)

@Serializable
data class SatelliteDbResponse(val name: String, val norad_id: Int, val launch_date: String)

fun main() {
    // Підключення до БД
    Database.connect(
            url = "jdbc:postgresql://localhost:5432/spacedata",
            driver = "org.postgresql.Driver",
            user = "admin",
            password = "admin_pass"
    )

    // Створення таблиць
    transaction { SchemaUtils.create(Satellites) }

    embeddedServer(Netty, port = 8080, host = "0.0.0.0", module = Application::module)
            .start(wait = true)
}

fun Application.module() {
    install(CORS) {
        anyHost()
        allowMethod(HttpMethod.Get)
        allowMethod(HttpMethod.Post)
        allowMethod(HttpMethod.Options)
        allowHeader(HttpHeaders.ContentType)
        allowHeader(HttpHeaders.Authorization)
    }

    install(ContentNegotiation) {
        json()
    }

    routing {
        get("/") { call.respond(mapOf("service" to "satellite-tracker", "status" to "online")) }

        get("/satellites") {
            val result = transaction {
                Satellites.selectAll().map {
                    SatelliteDbResponse(
                            name = it[Satellites.name],
                            norad_id = it[Satellites.noradId],
                            launch_date = it[Satellites.launchDate]
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

        get("/fetch-tle") {
            val client = HttpClient(Apache)
            try {
                // Використовуємо Celestrak для відкритого доступу до TLE (без авторизації як у
                // Space-Track)
                val response: HttpResponse =
                        client.get(
                                "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
                        )
                val tleData = response.bodyAsText()

                // Простий парсинг перших 10 супутників для демонстрації
                val lines = tleData.lines().filter { it.isNotBlank() }
                val parsedSatellites = mutableListOf<SatelliteTle>()

                for (i in 0 until minOf(lines.size, 30) step 3) {
                    if (i + 2 < lines.size) {
                        val name = lines[i].trim()
                        val line1 = lines[i + 1]
                        val line2 = lines[i + 2]

                        // Валідація: справжні TLE-рядки починаються з "1 " та "2 "
                        if (!line1.startsWith("1 ") || !line2.startsWith("2 ")) continue

                        // NORAD ID знаходиться у рядку 1, колонки 3-7
                        val noradIdStr = line1.substring(2, 7).trim()
                        parsedSatellites.add(
                                SatelliteTle(
                                        name = name,
                                        norad_id = noradIdStr,
                                        tle_line1 = line1,
                                        tle_line2 = line2
                                )
                        )
                    }
                }

                call.respond(TleResponse("success", parsedSatellites.size, parsedSatellites))
            } catch (e: Exception) {
                call.respond(mapOf("status" to "error", "message" to e.localizedMessage))
            } finally {
                client.close()
            }
        }
    }
}
