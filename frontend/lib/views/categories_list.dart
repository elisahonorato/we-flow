import 'package:flutter/material.dart';
import 'package:frontend/models/category.dart';
import 'package:frontend/services/auth_services.dart';
import 'package:frontend/services/category_service.dart';

class CategoriesList extends StatefulWidget {
  @override
  _CategoriesListState createState() => _CategoriesListState();
}

class _CategoriesListState extends State<CategoriesList> {
  final AuthService _authService = AuthService();
  final CategoryService _categoryService = CategoryService();

  Future<List<Category>> _fetchCategories() async {
    try {
      final categories = await _categoryService.fetchCategories();
      return categories;
    } catch (e) {
      print('Connection failed with error: $e');
      throw Exception('Connection failed: $e');
    }
  }

  // Función para mapear el nombre del icono a IconData
  IconData getIconData(String iconName) {
    switch (iconName) {
      case 'local_hospital':
        return Icons.local_hospital;
      case 'directions_run':
        return Icons.directions_run;
      case 'restaurant':
        return Icons.restaurant;
      case 'accessibility':
        return Icons.accessibility;
      case 'home':
        return Icons.home;
      case 'medication':
        return Icons.medication;
      case 'psychology':
        return Icons.psychology;
      case 'visibility':
        return Icons.visibility;
      case 'fitness_center':
        return Icons.fitness_center;
      default:
        return Icons.help;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Selecciona una categoría'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await _authService.logout();
              Navigator.pushReplacementNamed(context, '/');
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Category>>(
        future: _fetchCategories(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final categories = snapshot.data!;
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10.0),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10.0,
                  mainAxisSpacing: 10.0,
                ),
                itemCount: categories.length,
                itemBuilder: (context, index) {
                  final category = categories[index];
                  return Card(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(getIconData(category.icon), size: 40.0),
                        const SizedBox(height: 20),
                        Text(category.title, textAlign: TextAlign.center),
                      ],
                    ),
                  );
                },
              ),
            );
          }
        },
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today), label: 'Recordar'),
          BottomNavigationBarItem(icon: Icon(Icons.check_circle), label: 'Evaluar'),
          BottomNavigationBarItem(icon: Icon(Icons.fitness_center), label: 'Entrenar'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Mis Datos'),
        ],
      ),
    );
  }
}
