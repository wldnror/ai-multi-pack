private fun sendUDPData(data: ByteArray) {
    try {
        val ipAddress = InetAddress.getByName("라즈베리파이의_IP_주소")
        val packet = DatagramPacket(data, data.size, ipAddress, udpPort)
        udpSocket.send(packet)
    } catch (e: UnknownHostException) {
        // 호스트 이름을 해결할 수 없는 경우 사용자에게 메시지 표시
        Toast.makeText(this, "Unable to resolve host. Please check the IP address.", Toast.LENGTH_SHORT).show()
        e.printStackTrace()
    } catch (e: Exception) {
        e.printStackTrace()
    }
}
