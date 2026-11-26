class SnakeCaseAliasMixin:
    """
    Permite que un serializer acepte también los nombres en snake_case.

    La app Android manda los campos en camelCase (`producerName`), pero otros clientes pueden mandar
    `producer_name`. Cada serializer declara sus equivalencias en `snake_case_aliases`:

        class ProductSerializer(SnakeCaseAliasMixin, serializers.ModelSerializer):
            snake_case_aliases = {'producer_name': 'producerName'}

    Si llegan los dos nombres, gana el camelCase.
    """

    snake_case_aliases = {}

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        for snake_name, camel_name in self.snake_case_aliases.items():
            if snake_name in data and camel_name not in data:
                data[camel_name] = data[snake_name]
        return super().to_internal_value(data)
