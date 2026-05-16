import org.jetbrains.compose.web.renderComposable
import org.jetbrains.compose.web.dom.*
import org.jetbrains.compose.web.css.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.js.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import androidx.compose.runtime.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue

@Serializable
data class TleResponse(val status: String, val count: Int, val data: List<SatelliteTle>)

@Serializable
data class SatelliteTle(val name: String, val norad_id: String, val tle_line1: String, val tle_line2: String)

@Serializable
data class SpaceWeatherResponse(val status: String, val source: String, val latest_kp_index: KpIndex)

@Serializable
data class KpIndex(val time_tag: String, val Kp: Double)

val httpClient = HttpClient(Js) {
    install(ContentNegotiation) {
        json(Json { ignoreUnknownKeys = true })
    }
}

@Composable
fun App() {
    val satellitesState = remember { mutableStateOf<List<SatelliteTle>>(emptyList()) }
    val kpIndexState = remember { mutableStateOf<Double?>(null) }
    val loadingState = remember { mutableStateOf(false) }
    val errorMessageState = remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Div({ style { padding(20.px); fontFamily("Arial, sans-serif"); backgroundColor(Color("#1e1e1e")); color(Color("white")); minHeight(100.vh) } }) {
        H1 { Text("Space Data Dashboard 🌌") }
        
        Div({ style { display(DisplayStyle.Flex); justifyContent(JustifyContent.SpaceBetween); marginBottom(20.px) } }) {
            Button(attrs = {
                onClick {
                    scope.launch {
                        loadingState.value = true
                        errorMessageState.value = null
                        try {
                            val weatherRes: SpaceWeatherResponse = httpClient.get("http://localhost:8001/noaa-kp-index").body()
                            kpIndexState.value = weatherRes.latest_kp_index.Kp
                            
                            val satRes: TleResponse = httpClient.get("http://localhost:8080/fetch-tle").body()
                            satellitesState.value = satRes.data
                        } catch (e: Exception) {
                            errorMessageState.value = e.message
                        } finally {
                            loadingState.value = false
                        }
                    }
                }
                style { padding(10.px); backgroundColor(Color("#4CAF50")); color(Color("white")); border(0.px); cursor("pointer") }
            }) {
                Text("Refresh Data")
            }
            
            if (kpIndexState.value != null) {
                Div({ style { padding(10.px); backgroundColor(if (kpIndexState.value!! > 4.0) Color("red") else Color("green")); borderRadius(5.px) } }) {
                    Text("Kp-Index: ${kpIndexState.value}")
                }
            }
        }
        
        if (loadingState.value) {
            P { Text("Loading data from microservices...") }
        } else if (errorMessageState.value != null) {
            P({ style { color(Color("red")) } }) { Text("Error: ${errorMessageState.value}") }
        } else {
            H3 { Text("Active Satellites (${satellitesState.value.size}):") }
            Div({ style { display(DisplayStyle.Flex); flexDirection(FlexDirection.Column); gap(10.px) } }) {
                satellitesState.value.forEach { sat ->
                    Div({ style { backgroundColor(Color("#2d2d2d")); padding(15.px); borderRadius(8.px) } }) {
                        B { Text(sat.name) }
                        Br()
                        Small { Text("NORAD ID: ${sat.norad_id}") }
                        Br()
                        Pre({ style { margin(0.px); fontSize(12.px); color(Color("lightgray")) } }) {
                            Text(sat.tle_line1 + "\n" + sat.tle_line2)
                        }
                    }
                }
            }
        }
    }
}

fun main() {
    renderComposable(rootElementId = "root") {
        App()
    }
}

