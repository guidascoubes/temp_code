#include <OneWire.h>
#include <DallasTemperature.h>

// *******ANALOG DEF*******
#define ANALOG_RANGE 4096
#define TENSAO_ESP 3.3
#define TENSAO_PIN_NTC 34
#define TENSAO_PIN_LM 39
#define ONE_WIRE_BUS 32
#define RELAY_PIN 18  // Definindo o pino onde o relay está conectado

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);          // Iniciar a comunicação serial
  pinMode(TENSAO_PIN_LM, INPUT);
  pinMode(RELAY_PIN, OUTPUT);    // Configura o pino do relay como saída
  digitalWrite(RELAY_PIN, LOW);  // Garante que o relay começa desligado
  sensors.begin();
}

void loop() {
  float valortensao_NTC,valortensao_LM, Temperatura_NTC, temperaturaDS;
  sensors.requestTemperatures(); 
  valortensao_NTC = ReadAnalog(TENSAO_PIN_NTC);//ReadAnalog trata já de multiplicar pela tensao e dividir pelo range
  valortensao_LM = ReadAnalog(TENSAO_PIN_LM);
  temperaturaDS = sensors.getTempCByIndex(0);
  // Enviar os valores no formato esperado (valores separados por vírgulas)
  EnviaValoresSerial(valortensao_NTC, valortensao_LM, temperaturaDS - 5,2);
  VerificarMensagemRelay();
}

// **********ANALOG -> 3.3 VOLTS**********
float ReadAnalog(int pin) {
  float valAnalog = analogRead(pin);
  float valTensao = (valAnalog / ANALOG_RANGE) * TENSAO_ESP;
  return valTensao;
}
// verifica se e suposto ligar ou desligar o relay
void VerificarMensagemRelay() {
  if (Serial.available() > 0) {                     // Verifica se há dados disponíveis para ler
    String comando = Serial.readStringUntil('\n');  // Lê até a nova linha
    comando.trim();                                 // Remove espaços em branco extras

    if (comando == "RELAY_ON") {          // Verifica se o comando é para ligar o relay
      digitalWrite(RELAY_PIN, HIGH);      // Liga o relay
    } else if (comando == "RELAY_OFF") {  // Verifica se o comando é para desligar o relay
      digitalWrite(RELAY_PIN, LOW);       // Desliga o relay
    }
  }
}

void EnviaValoresSerial(float sensorNTC, float sensorLM35, float sensorDS18B20, int numCasasDecimais) {
  Serial.print(sensorNTC, numCasasDecimais); 
  Serial.print(",");
  Serial.print(sensorLM35, numCasasDecimais); 
  Serial.print(",");
  Serial.println(sensorDS18B20, numCasasDecimais);
  
  delay(500);
}