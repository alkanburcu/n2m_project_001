from rest_framework import serializers

from .models import Todo
from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
            model = Todo
    
            fields = ("id","user","title","completed","created_at","updated_at",)
    
            read_only_fields = ("id","user","created_at","updated_at",)

    def validate(self, attrs):
        if self.instance is not None:
            requested_user = attrs.get("user")

            if (
                requested_user is not None
                and requested_user != self.instance.user
            ):
                raise serializers.ValidationError(
                    {
                        "user": (
                            "Todo ownership cannot be changed."
                        )
                    }
                )

        return attrs