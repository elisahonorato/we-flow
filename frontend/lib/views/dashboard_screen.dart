import 'package:flutter/material.dart';
import 'package:frontend/sections/categories_section.dart';
import 'package:frontend/views/login_screen.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/sections/scroll_section.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class ScrollWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: TextRecomendationSection(),
    );
  }
}

class CategoriesWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: CategoriesSection(),
    );
  }
}

class EvaluateSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Evaluar Sección'),
    );
  }
}

class TrainSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Entrenar Sección'),
    );
  }
}

class MyDataSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text('Mis Datos Sección'),
    );
  }
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;
  bool _isHomeSelected = false; // Estado adicional para la casita

  List<Color> _iconColors = List.generate(5, (index) => Colors.grey);

  final AuthService _authService = AuthService();

  final List<Widget> _widgetOptions = <Widget>[
    ScrollWidget(),
    EvaluateSection(),
    TrainSection(),
    MyDataSection(),
    CategoriesWidget(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _isHomeSelected = false;

      // Actualizar colores: blanco si está seleccionado, gris si no
      for (int i = 0; i < _iconColors.length; i++) {
        _iconColors[i] = i == index + 1 ? Colors.black : Colors.grey;
      }
    });
  }

  Future<void> _logout() async {
    await _authService.logout();
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (context) => LoginScreen(),
      ),
    );
  }

  void _onFabPressed() {
    setState(() {
      _isHomeSelected = true;

      _iconColors =
          List.generate(5, (index) => index == 0 ? Colors.grey : Colors.grey);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                height: 120.0,
                color: Colors.yellow,
              ),
              Positioned(
                top: 80.0,
                left: MediaQuery.of(context).size.width / 2 - 40,
                child: Container(
                  width: 100.0,
                  height: 100.0,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        spreadRadius: 2,
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
              ),
              Positioned(
                top: 40.0,
                right: 20.0,
                child: IconButton(
                  icon: Icon(Icons.logout, color: Colors.black),
                  onPressed: _logout,
                ),
              ),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 20.0,
                vertical: 10.0,
              ),
              child: Material(
                elevation: 4.0,
                borderRadius: BorderRadius.circular(10.0),
                shadowColor: Colors.black.withOpacity(0.2),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10.0),
                  ),
                  child: _isHomeSelected
                      ? CategoriesWidget() // Muestra la vista de la casita
                      : _widgetOptions.elementAt(
                          _selectedIndex), // Muestra la vista seleccionada del BottomNavigationBar
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor:
            Colors.grey, // Esto colorea el texto del ítem seleccionado
        unselectedItemColor:
            Colors.grey, // Esto colorea el texto del ítem no seleccionado
        selectedLabelStyle: TextStyle(
          fontWeight:
              FontWeight.normal, // Texto en negrita cuando está seleccionado
          fontSize: 12, // Tamaño de fuente para el texto seleccionado
        ),
        unselectedLabelStyle: TextStyle(
          fontWeight:
              FontWeight.normal, // Texto normal cuando no está seleccionado
          fontSize: 12, // Tamaño de fuente para el texto no seleccionado
        ),

        items: <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.bookmark, color: _iconColors[1]),
            label: 'Recordar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.star, color: _iconColors[2]),
            label: 'Evaluar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center, color: _iconColors[3]),
            label: 'Entrenar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person, color: _iconColors[4]),
            label: 'Mis Datos',
          ),
        ],
        type: BottomNavigationBarType.fixed,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _onFabPressed,
        child: Icon(Icons.home,
            color: _isHomeSelected ? Colors.black : Colors.grey),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }
}

void main() => runApp(MaterialApp(
      home: DashboardScreen(),
      routes: {
        '/login': (context) => LoginScreen(),
      },
    ));
