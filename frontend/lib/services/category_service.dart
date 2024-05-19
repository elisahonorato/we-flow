import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/category.dart';

class CategoryService {
  static const String _baseUrl = 'http://tu-direccion-backend/api/categorias';

  static Future<List<Category>> fetchCategories() async {
    final response = await http.get(Uri.parse(_baseUrl));

    if (response.statusCode == 200) {
      List jsonResponse = json.decode(response.body)['categories'];
      return jsonResponse
          .map((category) => Category.fromJson(category))
          .toList();
    } else {
      throw Exception('Failed to load categories');
    }
  }
}
