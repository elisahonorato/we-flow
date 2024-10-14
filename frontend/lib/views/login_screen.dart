import 'package:flutter/material.dart';
import 'package:frontend/services/auth_services.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final AuthService _authService = AuthService();

  void _login() async {
    try {
      String username = _usernameController.text;
      String password = _passwordController.text;

      await _authService.login(username, password);

      // Navegar a la pantalla principal si el login es exitoso
      Navigator.pushReplacementNamed(context, '/dashboard');
    } catch (e) {
      // Manejar error de inicio de sesión
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.yellowAccent[100], // Fondo amarillo
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Logo como imagen PNG
            Center(
              child: Image.asset(
                'assets/general/logo.png', // Ruta de la imagen PNG
                height: 80, // Ajusta el tamaño según sea necesario
              ),
            ),
            const SizedBox(height: 20),
            // Título
            const Center(
              child: Text(
                'We train',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                ),
              ),
            ),
            const SizedBox(height: 8),
            // Subtítulo
            const Center(
              child: Text(
                'Plataforma multidimensional\nprevención de caídas en personas mayores.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.black87,
                ),
              ),
            ),
            const SizedBox(height: 40),
            // Campo de nombre de usuario
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(
                labelText: 'Username',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            // Campo de contraseña
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(
                labelText: 'Password',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(),
              ),
              obscureText: true,
            ),
            const SizedBox(height: 40),
            // Botón de inicio de sesión
            ElevatedButton(
              onPressed: _login,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(fontSize: 18),
              ),
              child: const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}