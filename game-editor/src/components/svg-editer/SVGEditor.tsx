import React, { useState, useRef, useEffect } from 'react';
import { storage } from '../../store/game-store';
import { observer } from 'mobx-react-lite';
import { SelectableEntity } from '../../models/drow-models';
import { runInAction } from 'mobx';

const SVGEditor = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const { selectedObject } = storage;
  const [viewBox, setViewBox] = useState({ x: 0, y: 0, width: 2000, height: 2000 });
  const [scale, setScale] = useState(1);
  const [listForRendering, setListForRendering] = useState<SelectableEntity[]>([]);
  const [dragState, setDragState] = useState<{
    type: 'object' | 'pan';
    startX: number;
    startY: number;
    objectStartX: number;
    objectStartY: number;
  } | null>(null);

  const [resizeState, setResizeState] = useState<{
    direction: 'n' | 'e' | 's' | 'w' | 'ne' | 'nw' | 'se' | 'sw' | null;
    startWidth: number;
    startHeight: number;
    startX: number;
    startY: number;
  }>({ direction: null, startWidth: 0, startHeight: 0, startX: 0, startY: 0 });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+C
      if (e.ctrlKey && e.key === 'c' && selectedObject) {
        storage.copyToClipboard(selectedObject);
        e.preventDefault();
      }

      // Ctrl+V
      if (e.ctrlKey && e.key === 'v' && storage.clipboard) {
        const pastedObj = storage.pasteFromClipboard();
        if (pastedObj) {
          storage.setSelectedObject(pastedObj);
        }
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedObject]);

  useEffect(() => {
    setListForRendering([...storage.entities, ...storage.grounds, ...storage.items]);
  }, [storage.entities.length, storage.grounds.length, storage.items.length]);

  useEffect(() => {
    storage.windowCoordinates = {
      x: viewBox.x + 100,
      y: viewBox.y + 100,
    };
  }, [viewBox]);

  // Преобразование экранных координат в SVG координаты
  const getSVGPoint = (clientX: number, clientY: number) => {
    if (!svgRef.current) return { x: 0, y: 0 };

    const pt = svgRef.current.createSVGPoint();
    pt.x = clientX;
    pt.y = clientY;
    return pt.matrixTransform(svgRef.current.getScreenCTM()?.inverse());
  };

  const handleMouseDown = (e: React.MouseEvent, obj?: SelectableEntity) => {
    if (e.target instanceof SVGRectElement && obj) {
      const svgPoint = getSVGPoint(e.clientX, e.clientY);
      storage.setSelectedObject(obj);

      // Определяем область клика (углы/границы или центр)
      const handleSize = 8 / scale; // Размер области для ресайза с учетом масштаба
      const isLeft = Math.abs(svgPoint.x - obj.x) < handleSize;
      const isRight = Math.abs(svgPoint.x - (obj.x + obj.width)) < handleSize;
      const isTop = Math.abs(svgPoint.y - obj.y) < handleSize;
      const isBottom = Math.abs(svgPoint.y - (obj.y + obj.height)) < handleSize;

      if (isLeft && isTop && !e.ctrlKey) {
        setResizeState({
          direction: 'nw',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isRight && isTop && !e.ctrlKey) {
        setResizeState({
          direction: 'ne',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isLeft && isBottom && !e.ctrlKey) {
        setResizeState({
          direction: 'sw',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isRight && isBottom && !e.ctrlKey) {
        setResizeState({
          direction: 'se',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isLeft && !e.ctrlKey) {
        setResizeState({
          direction: 'w',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isRight && !e.ctrlKey) {
        setResizeState({
          direction: 'e',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isTop && !e.ctrlKey) {
        setResizeState({
          direction: 'n',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else if (isBottom && !e.ctrlKey) {
        setResizeState({
          direction: 's',
          startWidth: obj.width,
          startHeight: obj.height,
          startX: svgPoint.x,
          startY: svgPoint.y,
        });
      } else {
        // Обычное перемещение
        setDragState({
          type: 'object',
          startX: svgPoint.x,
          startY: svgPoint.y,
          objectStartX: obj.x,
          objectStartY: obj.y,
        });
      }

      e.stopPropagation();
      e.preventDefault();
    } else if (e.button === 1 || e.ctrlKey) {
      // Панорамирование
      setDragState({
        type: 'pan',
        startX: e.clientX,
        startY: e.clientY,
        objectStartX: viewBox.x,
        objectStartY: viewBox.y,
      });
      e.preventDefault();
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!svgRef.current) return;

    const svgPoint = getSVGPoint(e.clientX, e.clientY);

    if (resizeState.direction && selectedObject) {
      const { direction, startWidth, startHeight, startX, startY } = resizeState;
      const deltaX = svgPoint.x - startX;
      const deltaY = svgPoint.y - startY;

      let newWidth = startWidth;
      let newHeight = startHeight;
      let newX = selectedObject.x;
      let newY = selectedObject.y;

      switch (direction) {
        case 'e': // восток - меняем только ширину
          newWidth = Math.max(10, startWidth + deltaX);
          break;
        case 'w': // запад - меняем ширину и позицию X
          newWidth = Math.max(10, startWidth - deltaX);
          newX = selectedObject.x + deltaX;
          break;
        case 's': // юг - меняем только высоту
          newHeight = Math.max(10, startHeight + deltaY);
          break;
        case 'n': // север - меняем высоту и позицию Y
          newHeight = Math.max(10, startHeight - deltaY);
          newY = selectedObject.y + deltaY;
          break;
        case 'ne': // северо-восток
          newWidth = Math.max(10, startWidth + deltaX);
          newHeight = Math.max(10, startHeight - deltaY);
          newY = selectedObject.y + deltaY;
          break;
        case 'nw': // северо-запад
          newWidth = Math.max(10, startWidth - deltaX);
          newHeight = Math.max(10, startHeight - deltaY);
          newX = selectedObject.x + deltaX;
          newY = selectedObject.y + deltaY;
          break;
        case 'se': // юго-восток
          newWidth = Math.max(10, startWidth + deltaX);
          newHeight = Math.max(10, startHeight + deltaY);
          break;
        case 'sw': // юго-запад
          newWidth = Math.max(10, startWidth - deltaX);
          newHeight = Math.max(10, startHeight + deltaY);
          newX = selectedObject.x + deltaX;
          break;
      }

      runInAction(() => {
        selectedObject.width = newWidth;
        selectedObject.height = newHeight;
        selectedObject.x = newX;
        selectedObject.y = newY;

        // Обновляем начальные координаты для следующего движения
        if (direction.includes('n') || direction.includes('w')) {
          setResizeState(prev => ({
            ...prev,
            startX: svgPoint.x,
            startY: svgPoint.y,
            startWidth: newWidth,
            startHeight: newHeight,
          }));
        }
      });
    } else if (dragState?.type === 'object' && selectedObject) {
      if (
        dragState.objectStartX + (svgPoint.x - dragState.startX) < 0 ||
        dragState.objectStartY + (svgPoint.y - dragState.startY) < 0
      ) {
        return;
      }
      runInAction(() => {
        selectedObject.x = dragState.objectStartX + (svgPoint.x - dragState.startX);
        selectedObject.y = dragState.objectStartY + (svgPoint.y - dragState.startY);
      });
    } else if (dragState?.type === 'pan') {
      const dx = (e.clientX - dragState.startX) / scale;
      const dy = (e.clientY - dragState.startY) / scale;

      setViewBox({
        ...viewBox,
        x: dragState.objectStartX - dx,
        y: dragState.objectStartY - dy,
      });
    }
  };

  const handleMouseUp = () => {
    setDragState(null);
    setResizeState({ direction: null, startWidth: 0, startHeight: 0, startX: 0, startY: 0 });
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();

    if (!svgRef.current) return;

    const svgPoint = getSVGPoint(e.clientX, e.clientY);
    const delta = -e.deltaY / 500;
    const newScale = Math.min(Math.max(0.1, scale * (1 + delta)), 5);

    setViewBox(prev => ({
      x: svgPoint.x - (svgPoint.x - prev.x) * (newScale / scale),
      y: svgPoint.y - (svgPoint.y - prev.y) * (newScale / scale),
      width: prev.width,
      height: prev.height,
    }));

    setScale(newScale);
  };

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [dragState, resizeState, selectedObject]);

  return (
    <div style={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
        onMouseDown={handleMouseDown}
        onWheel={handleWheel}
        style={{ cursor: getCursor() }}
      >
        <defs>
          <pattern id="grid" width={100} height={100} patternUnits="userSpaceOnUse">
            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#eee" strokeWidth="10" />
          </pattern>
        </defs>

        <rect
          x="-100000"
          y="-100000"
          width="200000"
          height="200000"
          fill="url(#grid)"
          onClick={() => {
            storage.selectedObject = null;
          }}
        />

        {listForRendering.map((obj, index) => {
          return (
            <rect
              key={index}
              x={obj.x}
              y={obj.y}
              width={obj.width}
              height={obj.height}
              fill={`rgb(${obj.color.join(',')})`}
              style={{ cursor: 'move' }}
              stroke="black"
              strokeWidth={storage.selectedObject === obj ? 10 : 0}
              onMouseDown={(event): void => handleMouseDown(event, obj)}
            />
          );
        })}
      </svg>

      <div
        style={{
          position: 'absolute',
          bottom: 20,
          right: 20,
          background: 'white',
          padding: '5px 10px',
          borderRadius: 5,
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}
      >
        <button
          onClick={() => {
            const newScale = Math.min(scale + 0.1, 5);
            setScale(newScale);
            setViewBox({
              ...viewBox,
              x: viewBox.x * (scale / newScale),
              y: viewBox.y * (scale / newScale),
              width: viewBox.width * (scale / newScale),
              height: viewBox.height * (scale / newScale),
            });
          }}
        >
          +
        </button>
        <span>{Math.round(scale * 100)}%</span>
        <button
          onClick={() => {
            const newScale = Math.max(scale - 0.1, 0.1);
            setScale(newScale);
            setViewBox({
              ...viewBox,
              x: viewBox.x * (scale / newScale),
              y: viewBox.y * (scale / newScale),
              width: viewBox.width * (scale / newScale),
              height: viewBox.height * (scale / newScale),
            });
          }}
        >
          -
        </button>
      </div>
    </div>
  );

  function getCursor() {
    if (dragState?.type === 'pan') return 'grabbing';
    if (resizeState.direction) {
      switch (resizeState.direction) {
        case 'n':
        case 's':
          return 'ns-resize';
        case 'e':
        case 'w':
          return 'ew-resize';
        case 'ne':
        case 'sw':
          return 'nesw-resize';
        case 'nw':
        case 'se':
          return 'nwse-resize';
      }
    }
    return 'default';
  }
};

export default observer(SVGEditor);
