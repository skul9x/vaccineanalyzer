from PySide6.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint, Qt

class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_direction = Qt.Horizontal
        self.m_speed = 300
        self.m_animation_type = "fade" 
        self.m_now_animating = False
        self.m_next_index = 0

    def setAnimation(self, type_name):
        self.m_animation_type = type_name

    def setCurrentIndex(self, index):
        if self.currentIndex() == index:
            return
        if self.m_now_animating:
            return
        
        self.m_next_index = index
        self.animate_switch(index)

    def animate_switch(self, index):
        self.m_now_animating = True
        
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        next_widget.setGeometry(0, 0, self.width(), self.height())
        
        if self.m_animation_type == "fade":
            self.fade_transition(current_widget, next_widget)
        else:
            super().setCurrentIndex(index)
            self.m_now_animating = False

    def fade_transition(self, current_widget, next_widget):
        next_widget.show()
        next_widget.raise_()
        
        effect_current = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(effect_current)
        
        effect_next = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(effect_next)
        effect_next.setOpacity(0)
        
        anim_current = QPropertyAnimation(effect_current, b"opacity")
        anim_current.setDuration(self.m_speed)
        anim_current.setStartValue(1)
        anim_current.setEndValue(0)
        
        anim_next = QPropertyAnimation(effect_next, b"opacity")
        anim_next.setDuration(self.m_speed)
        anim_next.setStartValue(0)
        anim_next.setEndValue(1)
        
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(anim_current)
        self.anim_group.addAnimation(anim_next)
        
        self.anim_group.finished.connect(lambda: self.on_animation_finished(next_widget, current_widget))
        self.anim_group.start()

    def on_animation_finished(self, next_widget, current_widget):
        super().setCurrentIndex(self.m_next_index)
        current_widget.hide()
        current_widget.setGraphicsEffect(None)
        next_widget.setGraphicsEffect(None)
        self.m_now_animating = False